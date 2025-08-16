from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ArtifactRead(BaseModel):
    id: UUID
    run_id: UUID
    name: str
    s3_key: str
    size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArtifactPresignRequest(BaseModel):
    run_id: UUID
    name: str
    size_bytes: int
