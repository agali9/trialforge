from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.experiment import Experiment
from app.models.run import Run
from app.models.user import User
from app.schemas.run import RunCreate, RunRead, RunUpdate

router = APIRouter(prefix="/runs", tags=["runs"])


async def _get_scoped_run(run_id: str, current_user: User, db: AsyncSession) -> Run:
    query = (
        select(Run)
        .join(Experiment, Experiment.id == Run.experiment_id)
        .where(Run.id == run_id, Experiment.workspace_id == current_user.workspace_id)
    )
    result = await db.execute(query)
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/experiment/{experiment_id}", response_model=list[RunRead])
async def list_runs(experiment_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    exp = await db.execute(select(Experiment).where(Experiment.id == experiment_id, Experiment.workspace_id == current_user.workspace_id))
    if exp.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Wrong workspace")
    result = await db.execute(select(Run).where(Run.experiment_id == experiment_id))
    return list(result.scalars().all())


@router.post("", response_model=RunRead)
async def create_run(payload: RunCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    exp = await db.execute(select(Experiment).where(Experiment.id == payload.experiment_id, Experiment.workspace_id == current_user.workspace_id))
    if exp.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Wrong workspace")
    run = Run(experiment_id=payload.experiment_id, name=payload.name, hyperparameters=payload.hyperparameters)
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


@router.get("/{run_id}", response_model=RunRead)
async def get_run(run_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _get_scoped_run(run_id, current_user, db)


@router.patch("/{run_id}", response_model=RunRead)
async def update_run(run_id: str, payload: RunUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    run = await _get_scoped_run(run_id, current_user, db)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(run, key, value)
    if payload.status == "completed" and payload.finished_at is None:
        run.finished_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(run)
    return run


@router.delete("/{run_id}", status_code=204)
async def delete_run(run_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    run = await _get_scoped_run(run_id, current_user, db)
    await db.delete(run)
    await db.commit()
