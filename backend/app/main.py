from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.routers import artifacts, auth, experiments, metrics, runs, ws

app = FastAPI(title="TrialForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def initialize_database() -> None:
    async with engine.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
                    metric_name VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    step INTEGER NOT NULL,
                    value DOUBLE PRECISION NOT NULL
                )
                """
            )
        )
        await conn.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS ix_metrics_run_metric_step
                ON metrics (run_id, metric_name, step, timestamp)
                """
            )
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(experiments.router)
app.include_router(runs.router)
app.include_router(metrics.router)
app.include_router(artifacts.router)
app.include_router(ws.router)
