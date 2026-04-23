"""FastAPI application entry point."""

import logging

from fastapi import FastAPI

from app.config import settings


logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

app = FastAPI(title="Notify Health WhatsApp Prototype", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    """Log the active environment on startup."""
    logger.info("Starting up — log_level=%s database=%s", settings.log_level, settings.database_url)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check used by Railway and manual curl tests."""
    return {"status": "ok", "version": "0.1.0"}
