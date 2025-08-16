from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.auth import Token, UserCreate, UserMe, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    workspace = Workspace(name=payload.workspace_name or "Default Workspace", slug=payload.workspace_slug or payload.email.split("@")[0])
    db.add(workspace)
    await db.flush()
    user = User(workspace_id=workspace.id, email=payload.email, hashed_password=hash_password(payload.password), role="owner")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id), "workspace_id": str(user.workspace_id), "role": user.role})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserMe)
async def me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_result = await db.execute(select(Workspace).where(Workspace.id == current_user.workspace_id))
    workspace = workspace_result.scalar_one_or_none()
    workspace_name = workspace.name if workspace else "Unknown Workspace"
    return UserMe(email=current_user.email, workspace_name=workspace_name)
