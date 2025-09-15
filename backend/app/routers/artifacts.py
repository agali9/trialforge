from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from minio import Minio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.artifact import Artifact
from app.models.run import Run
from app.models.user import User
from app.schemas.artifact import ArtifactPresignRequest, ArtifactRead

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)
BUCKET = "trialforge-artifacts"


def _storage_configured() -> bool:
    return settings.MINIO_ENDPOINT != "minio:9000"


def _raise_storage_not_configured() -> None:
    raise HTTPException(status_code=503, detail="Artifact storage is not configured")


@router.post("/presign")
async def presign_upload(payload: ArtifactPresignRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not _storage_configured():
        _raise_storage_not_configured()
    run = await db.execute(select(Run).where(Run.id == payload.run_id))
    if run.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if not minio_client.bucket_exists(BUCKET):
        minio_client.make_bucket(BUCKET)
    s3_key = f"{payload.run_id}/{uuid4()}-{payload.name}"
    artifact = Artifact(run_id=payload.run_id, name=payload.name, s3_key=s3_key, size_bytes=payload.size_bytes)
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    url = minio_client.get_presigned_url("PUT", BUCKET, s3_key)
    return {"artifact_id": str(artifact.id), "url": url}


@router.get("/{run_id}", response_model=list[ArtifactRead])
async def list_artifacts(run_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Artifact).where(Artifact.run_id == run_id))
    return list(result.scalars().all())


@router.get("/{artifact_id}/download")
async def download_artifact(artifact_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not _storage_configured():
        _raise_storage_not_configured()
    result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    url = minio_client.get_presigned_url("GET", BUCKET, artifact.s3_key)
    return {"url": url}
