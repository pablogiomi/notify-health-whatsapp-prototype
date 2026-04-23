"""SQLAlchemy 2.0 engine, session factory, and declarative base."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


engine = create_engine(
    settings.database_url,
    # SQLite requires this flag so the same connection can be used across
    # threads (FastAPI runs handlers in a thread pool by default).
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
