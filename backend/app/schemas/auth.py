from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    workspace_name: str | None = None
    workspace_slug: str | None = None


class UserRead(BaseModel):
    id: UUID
    workspace_id: UUID
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMe(BaseModel):
    email: EmailStr
    workspace_name: str
