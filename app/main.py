"""FastAPI application entry point."""

import logging

from fastapi import FastAPI

import app.models  # noqa: F401 — registers ORM models with Base before create_all
from app.config import settings
from app.db import Base, engine
from app.routers.send import router as send_router
from app.routers.webhook import router as webhook_router


logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

app = FastAPI(title="Notify Health WhatsApp Prototype", version="0.1.0")
app.include_router(send_router)
app.include_router(webhook_router)


@app.on_event("startup")
async def on_startup() -> None:
    """Create database tables and log the active environment."""
    Base.metadata.create_all(bind=engine)
    logger.info("Starting up — log_level=%s database=%s", settings.log_level, settings.database_url)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check used by Railway and manual curl tests."""
    return {"status": "ok", "version": "0.1.0"}
