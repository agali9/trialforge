from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import artifacts, auth, experiments, metrics, runs, ws

app = FastAPI(title="TrialForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
