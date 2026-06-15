from fastapi import FastAPI
from app.api.endpoints import api_router
from app.db import Base, postgres_engine
from app.utils import setup_logging
import app.models  

setup_logging()

app = FastAPI(
    title="AI News Bot",
    version="1.0",
    description="Automated Telegram news channel powered by FastAPI, Celery, RabbitMQ and OpenAI.",
)

app.include_router(router=api_router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    async with postgres_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)