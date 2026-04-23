"""SQLAlchemy 2.0 ORM models: Recipient, Message, MessageEvent."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Recipient(Base):
    """A person who may receive a WhatsApp reminder message."""

    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    whatsapp_reachable: Mapped[str] = mapped_column(String, nullable=False, default="unknown")
    last_attempted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="recipient")


class Message(Base):
    """One send attempt to a recipient; holds current delivery status and the Meta wamid."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipients.id"), nullable=False, index=True)
    template_name: Mapped[str] = mapped_column(String, nullable=False)
    template_language: Mapped[str] = mapped_column(String, nullable=False)
    meta_message_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True, index=True)
    current_status: Mapped[str] = mapped_column(String, nullable=False, default="queued")
    last_error_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    recipient: Mapped["Recipient"] = relationship("Recipient", back_populates="messages")
    events: Mapped[list["MessageEvent"]] = relationship("MessageEvent", back_populates="message")


class MessageEvent(Base):
    """Immutable record of a single status callback received from Meta."""

    __tablename__ = "message_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    error_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    raw_payload: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    message: Mapped["Message"] = relationship("Message", back_populates="events")
