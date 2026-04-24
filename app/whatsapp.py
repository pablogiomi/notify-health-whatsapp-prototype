"""Async client for the Meta WhatsApp Cloud API."""

import httpx

from app.config import settings


async def send_template_message(
    phone_number: str,
    template_name: str,
    template_language: str,
) -> dict:
    """POST a pre-approved template message to one recipient via Meta's Graph API.

    Returns the parsed JSON response on HTTP 200.
    Raises httpx.HTTPStatusError on any non-2xx response.
    """
    to = phone_number.lstrip("+")
    url = (
        f"https://graph.facebook.com"
        f"/{settings.whatsapp_graph_api_version}"
        f"/{settings.whatsapp_phone_number_id}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token.get_secret_value()}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": template_language},
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
