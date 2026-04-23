"""Router for POST /send — triggers a campaign run against all eligible recipients."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Message, Recipient
from app.whatsapp import send_template_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/send")
async def send_campaign(db: Session = Depends(get_db)) -> dict[str, int]:
    """Send the configured template to all recipients not known to be unreachable.

    Returns a summary dict with keys 'sent' and 'failed'.
    """
    recipients = (
        db.execute(select(Recipient).where(Recipient.whatsapp_reachable != "no"))
        .scalars()
        .all()
    )

    sent = 0
    failed = 0

    for recipient in recipients:
        try:
            response = await send_template_message(
                phone_number=recipient.phone_number,
                template_name=settings.campaign_template_name,
                template_language=settings.campaign_template_language,
            )
            wamid = response["messages"][0]["id"]
            message = Message(
                recipient_id=recipient.id,
                template_name=settings.campaign_template_name,
                template_language=settings.campaign_template_language,
                meta_message_id=wamid,
                current_status="sent",
            )
            sent += 1
        except Exception as exc:
            logger.error("Failed to send to recipient %s: %s", recipient.id, exc)
            message = Message(
                recipient_id=recipient.id,
                template_name=settings.campaign_template_name,
                template_language=settings.campaign_template_language,
                current_status="failed",
            )
            failed += 1

        recipient.last_attempted_at = datetime.utcnow()
        db.add(message)
        db.flush()

    db.commit()
    return {"sent": sent, "failed": failed}
