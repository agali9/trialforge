from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RunCreate(BaseModel):
    experiment_id: UUID
    name: str
    hyperparameters: dict | None = None


class RunUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    finished_at: datetime | None = None
    hyperparameters: dict | None = None


class RunRead(BaseModel):
    id: UUID
    experiment_id: UUID
    name: str
    status: str
    hyperparameters: dict | None
    notes: str | None
    started_at: datetime
    finished_at: datetime | None

    class Config:
        from_attributes = True
