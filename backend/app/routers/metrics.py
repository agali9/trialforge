import json

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.metrics import MetricBatch

router = APIRouter(prefix="/metrics", tags=["metrics"])
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.post("/batch")
async def batch_write(payload: MetricBatch, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    values = [
        {"run_id": str(payload.run_id), "metric_name": m.name, "step": m.step, "value": m.value, "timestamp": m.timestamp}
        for m in payload.metrics
    ]
    if values:
        await db.execute(
            text(
                """
                INSERT INTO metrics (run_id, metric_name, step, value, timestamp)
                VALUES (:run_id, :metric_name, :step, :value, :timestamp)
                ON CONFLICT (run_id, metric_name, step, timestamp)
                DO UPDATE SET value = EXCLUDED.value, timestamp = EXCLUDED.timestamp
                """
            ),
            values,
        )
        await db.commit()
        for item in values:
            await redis_client.publish(f"metrics:{item['run_id']}", json.dumps(item, default=str))
    return {"written": len(values)}


@router.get("/{run_id}/names")
async def metric_names(run_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT DISTINCT metric_name FROM metrics WHERE run_id = :run_id ORDER BY metric_name"), {"run_id": run_id})
    return [r[0] for r in result.fetchall()]


@router.get("/{run_id}")
async def metric_data(
    run_id: str,
    metric_names: str | None = Query(default=None),
    downsample: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if metric_names:
        names = [m.strip() for m in metric_names.split(",") if m.strip()]
    else:
        nresult = await db.execute(text("SELECT DISTINCT metric_name FROM metrics WHERE run_id = :run_id"), {"run_id": run_id})
        names = [r[0] for r in nresult.fetchall()]
    out = []
    for metric_name in names:
        if downsample:
            query = text(
                """
                WITH bucket_size AS (
                  SELECT CASE
                    WHEN (MAX(step) - MIN(step)) / 500.0 < 1 THEN 1
                    ELSE CEIL((MAX(step) - MIN(step)) / 500.0)::int
                  END AS step_bucket
                  FROM metrics
                  WHERE run_id = :run_id AND metric_name = :metric_name
                )
                SELECT MIN(step) as step, AVG(value) as value, time_bucket(make_interval(secs => (SELECT step_bucket FROM bucket_size)), timestamp) as bucket_time
                FROM metrics
                WHERE run_id = :run_id AND metric_name = :metric_name
                GROUP BY bucket_time
                ORDER BY bucket_time
                """
            )
        else:
            query = text(
                """
                SELECT step, value, timestamp as bucket_time
                FROM metrics
                WHERE run_id = :run_id AND metric_name = :metric_name
                ORDER BY step
                """
            )
        result = await db.execute(query, {"run_id": run_id, "metric_name": metric_name})
        points = [{"step": int(r.step), "value": float(r.value), "timestamp": r.bucket_time.isoformat()} for r in result.fetchall()]
        out.append({"metric_name": metric_name, "points": points})
    return out
