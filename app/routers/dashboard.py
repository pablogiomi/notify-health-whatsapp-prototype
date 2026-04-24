"""Router for GET /dashboard and GET /dashboard/table — server-rendered status monitor."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.db import get_db
from app.models import Message, Recipient

logger = logging.getLogger(__name__)

router = APIRouter()
# Defined here (not imported from main) to avoid the circular import
# that would result from main → dashboard → main.
templates = Jinja2Templates(directory="app/templates")


@dataclass
class RecipientRow:
    """View model for one row in the dashboard table."""

    name: Optional[str]
    phone_number: str
    whatsapp_reachable: str
    last_status: Optional[str]
    last_updated: Optional[datetime]


def _build_rows(db: Session) -> list[RecipientRow]:
    """Query all recipients ordered by id and attach their most recent message."""
    recipients = db.query(Recipient).order_by(Recipient.id).all()
    rows: list[RecipientRow] = []
    for recipient in recipients:
        message = (
            db.query(Message)
            .filter(Message.recipient_id == recipient.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        rows.append(
            RecipientRow(
                name=recipient.name,
                phone_number=recipient.phone_number,
                whatsapp_reachable=recipient.whatsapp_reachable,
                last_status=message.current_status if message else None,
                last_updated=message.updated_at if message else None,
            )
        )
    return rows


@router.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)) -> Response:
    """Render the full dashboard page showing all recipients and their latest message status."""
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "recipients": _build_rows(db),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        },
    )


@router.get("/dashboard/table")
async def dashboard_table(request: Request, db: Session = Depends(get_db)) -> Response:
    """Return the tbody fragment that HTMX swaps in on each 5-second poll."""
    return templates.TemplateResponse(
        request=request,
        name="dashboard_table.html",
        context={
            "recipients": _build_rows(db),
        },
    )
