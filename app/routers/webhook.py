"""Router for GET and POST /webhook — Meta verification handshake and status callbacks."""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Message, MessageEvent

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_signature(raw_body: bytes, sig_header: str, secret: str) -> bool:
    """Return True if the X-Hub-Signature-256 header matches the HMAC of raw_body."""
    if not sig_header.startswith("sha256="):
        return False
    computed = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={computed}", sig_header)


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> PlainTextResponse:
    """Handle Meta's one-time webhook verification handshake.

    Meta sends GET with hub.mode=subscribe and the verify token we configured.
    Echoing hub.challenge proves we control this endpoint.
    """
    if (
        hub_mode == "subscribe"
        and hub_verify_token == settings.whatsapp_webhook_verify_token
    ):
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403)


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Receive status-update callbacks from Meta, verify signature, and persist events.

    Always returns HTTP 200: non-200 triggers Meta retries for genuine payloads,
    and we don't want retries for spoofed ones either.
    """
    raw_body = await request.body()
    sig_header = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(
        raw_body, sig_header, settings.whatsapp_app_secret.get_secret_value()
    ):
        logger.warning("Webhook: signature verification failed, ignoring payload")
        return JSONResponse({"status": "ignored"}, status_code=200)

    payload = json.loads(raw_body)

    try:
        value = payload["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError):
        return {"status": "ok"}

    if "statuses" not in value:
        return {"status": "ok"}

    for status_update in value["statuses"]:
        wamid: str = status_update["id"]
        status: str = status_update["status"]
        errors: list = status_update.get("errors", [{}])
        error_code: Optional[int] = errors[0].get("code") if errors else None
        error_message: Optional[str] = errors[0].get("title") if errors else None
        occurred_at: datetime = datetime.utcfromtimestamp(
            int(status_update["timestamp"])
        )

        message = db.execute(
            select(Message).where(Message.meta_message_id == wamid)
        ).scalar_one_or_none()

        if message is None:
            logger.warning("Webhook: received status for unknown wamid=%s", wamid)
            continue

        message_event = MessageEvent(
            message_id=message.id,
            status=status,
            error_code=error_code,
            error_message=error_message,
            occurred_at=occurred_at,
            raw_payload=json.dumps(status_update),
        )

        message.current_status = status

        if status in ("delivered", "read"):
            message.recipient.whatsapp_reachable = "yes"
        elif status == "failed" and error_code in (131026, 131051):
            message.recipient.whatsapp_reachable = "no"

        db.add(message_event)
        db.flush()

        logger.info(
            "Webhook: wamid=%s status=%s recipient=%s",
            wamid,
            status,
            message.recipient.phone_number,
        )

    db.commit()
    return {"status": "ok"}
