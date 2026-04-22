# app/ — FastAPI application source

This directory will hold the Python source code of the prototype. It is empty on Day 1; code is added from Day 2 onward.

Expected layout (will be created as we go):

```
app/
├── __init__.py
├── main.py              # FastAPI application entry point
├── config.py            # Loads and validates environment variables
├── db.py                # SQLAlchemy engine, session, Base declarative
├── models.py            # Recipient, Message, MessageEvent models
├── whatsapp.py          # Thin async client around Meta's Graph API
├── webhooks.py          # Webhook verification + event handlers
├── campaigns.py         # "Run a campaign" logic
├── routers/
│   ├── send.py          # POST /send
│   ├── webhook.py       # GET + POST /webhook
│   └── dashboard.py     # GET /dashboard
└── templates/           # Jinja2 HTML templates for the dashboard
    └── dashboard.html
```

This is a plan, not a promise — it may evolve as we build.
