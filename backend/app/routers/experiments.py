from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.experiment import Experiment
from app.models.user import User
from app.schemas.experiment import ExperimentCreate, ExperimentRead

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=list[ExperimentRead])
async def list_experiments(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Experiment).where(Experiment.workspace_id == current_user.workspace_id))
    return list(result.scalars().all())


@router.post("", response_model=ExperimentRead)
async def create_experiment(payload: ExperimentCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    experiment = Experiment(workspace_id=current_user.workspace_id, name=payload.name, description=payload.description)
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    return experiment


@router.get("/{experiment_id}", response_model=ExperimentRead)
async def get_experiment(experiment_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id, Experiment.workspace_id == current_user.workspace_id))
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(experiment_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Experiment).where(Experiment.id == experiment_id, Experiment.workspace_id == current_user.workspace_id))
    experiment = result.scalar_one_or_none()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await db.delete(experiment)
    await db.commit()
