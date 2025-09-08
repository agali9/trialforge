import asyncio

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.auth import decode_access_token
from app.config import settings

router = APIRouter(tags=["ws"])
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.websocket("/ws/runs/{run_id}")
async def run_stream(websocket: WebSocket, run_id: str, token: str = Query(...)):
    decode_access_token(token)
    await websocket.accept()
    pubsub = redis_client.pubsub()
    channel = f"metrics:{run_id}"
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
