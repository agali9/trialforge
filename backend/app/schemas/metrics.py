from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    name: str
    step: int
    value: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricBatch(BaseModel):
    run_id: UUID
    metrics: list[MetricPoint]
