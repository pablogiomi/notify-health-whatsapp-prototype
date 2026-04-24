# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate the virtualenv (required before any Python command)
source .venv/bin/activate

# Run the dev server (auto-reload)
uvicorn app.main:app --reload

# Run all tests
pytest

# Run a single test file
pytest tests/test_webhooks.py

# Run a single test
pytest tests/test_webhooks.py::test_signature_verification

# Check for type errors (if mypy is added later)
# mypy app/
```

Dependencies are in `requirements.txt` (loosely pinned with `~=`). Install with `pip install -r requirements.txt`.

## Architecture

A FastAPI application that sends WhatsApp reminder messages via the Meta Cloud API and tracks delivery through webhooks.

**Four actors:** The app, a SQLite database (`app.db`), Meta's Graph API (`graph.facebook.com`), and recipient phones.

**Async message lifecycle:** The app sends a template to Meta and receives only a receipt (`wamid`). Actual delivery happens asynchronously — Meta calls back via webhooks. The `wamid` is the join key between outbound sends and inbound webhook events.

**Planned endpoints** (only `/health` exists today):

| Endpoint | Role |
|---|---|
| `POST /send` | Trigger a campaign; iterates recipients, sends template, records outcomes |
| `GET /webhook` | Meta's one-time verification handshake — echoes hub.challenge to prove URL ownership |
| `POST /webhook` | Receives status callbacks; verifies `X-Hub-Signature-256`, appends event, updates status |
| `GET /dashboard` | Server-rendered HTML with HTMX refresh showing per-recipient message state |
| `GET /health` | Liveness check |

**Database — three tables:**

- `recipients` — phone numbers with `whatsapp_reachable` (`unknown`/`yes`/`no`). Reachability is inferred from webhook outcomes (no pre-flight check exists on Meta's API).
- `messages` — one row per send attempt; holds both our internal `id` and Meta's `meta_message_id` (the `wamid`); `current_status` reflects the latest known state.
- `message_events` — append-only log of every webhook event; includes `raw_payload` (full Meta JSON, useful for debugging, flagged for removal in production).

**Module plan** (not all files exist yet):

```
app/
├── main.py          # FastAPI app + startup hook
├── config.py        # pydantic-settings; fails fast if env vars missing
├── db.py            # SQLAlchemy engine, SessionLocal, Base
├── models.py        # ORM models: Recipient, Message, MessageEvent
├── whatsapp.py      # Async httpx client wrapping Meta's Graph API
├── webhooks.py      # Signature verification + event handler dispatch
├── campaigns.py     # Campaign run logic (iterate recipients → send)
└── routers/
    ├── send.py
    ├── webhook.py
    └── dashboard.py
```

## Configuration

All secrets come from environment variables, loaded via `pydantic-settings` from a `.env` file. Copy `.env.example` → `.env` and fill in the Meta credentials. All required vars are declared in `app/config.py`; the app raises on startup if any are missing.

**Required vars:** `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_APP_SECRET`, `WHATSAPP_WEBHOOK_VERIFY_TOKEN`.

Graph API version is pinned to v25.0 (set in config.py default).

For local webhook testing, Meta needs a public URL — use ngrok to tunnel to `localhost:8000`.

## Working conventions

**Before writing any code**, read `docs/ARCHITECTURE.md` and the relevant section of `docs/DECISIONS.md`. The design is already decided — implement it, don't redesign it.

**Always show diffs for review before applying.** Never apply changes without the user confirming. Use the word "STOP" if you are waiting for confirmation.

**Do not add new packages** to requirements.txt without explicitly asking first. If you think a package would help, name it and wait for approval.

**Do not create endpoints, files, or database columns** not described in ARCHITECTURE.md without asking first.

**Type hints and docstrings are required** on every function and class. No exceptions.

**Never read or write the .env file.** Credentials are the user's responsibility.

## Test protocol

Run this protocol when Pablo says "test me", "knowledge check", or "run the test protocol". Also offer it at the end of any session where significant new concepts were covered.

### Structure

1. Generate 8–10 questions covering concepts from the current or most recent working session. Weight questions toward:
   - Concepts Pablo got wrong or flagged as unclear
   - The "why" behind decisions, not just the "what"
   - Edge cases and failure modes (these reveal real understanding)
   - At least one question requiring Pablo to write or describe actual code or a command

2. Present all questions at once. Wait for all answers before giving feedback.

3. Score each answer:
   - Full credit: correct reasoning, not just correct answer
   - Partial credit: right outcome, wrong or incomplete reasoning
   - Zero: incorrect, or "I don't know" (honest zero beats a guess)

4. Feedback format:
   - What was right and why
   - What was wrong and the correct explanation
   - One-line "remember this" summary for any score below 6/10

5. End with:
   - A score summary table
   - The two or three weakest areas to reinforce
   - Whether to run a follow-up test at the start of next session (recommend yes if average score below 7/10)

### Timing

- End of session: when significant new code or concepts were built
- Start of session: only if previous session ended with average below 7/10, or if more than 2 days have passed since last session
- Never run mid-session — it breaks coding flow

### Question bank guidance

Draw from these topic areas as relevant:
- Git operations and what they actually do internally
- Database concepts (sessions, transactions, flush vs commit, foreign keys, relationships, Base)
- HTTP and API concepts (status codes, headers, REST, async)
- WhatsApp API specifics (wamid, templates, webhooks, error codes)
- FastAPI patterns (dependencies, routers, request lifecycle)
- Python concepts introduced during coding (SecretStr, async/await, generators, type hints)
- Security concepts (HMAC, signature verification, SecretStr, environment variables)
- Architecture decisions — the "why" behind DR-001 through DR-016

## Key design decisions

- **Reachability is observed, not pre-checked** — Meta deprecated the `contacts` endpoint. Start everyone at `unknown`; first campaign transitions to `yes`/`no` based on webhook error codes (`131026`, `131051` = unreachable).
- **SQLite → Postgres migration is a connection-string swap** — SQLAlchemy abstracts the dialect; `connect_args` in `db.py` already handles the SQLite-specific thread flag conditionally.
- **Dashboard uses Jinja2 + HTMX** — no JS framework; server renders HTML fragments, HTMX refreshes the status column.
- **Webhook signature verification is mandatory** — `X-Hub-Signature-256` is checked on every `POST /webhook` using the app secret (DR-010 in `docs/DECISIONS.md`).
- **`raw_payload` stored during development** — full Meta webhook JSON kept for debugging; documented as a drop-candidate in production.

See `docs/ARCHITECTURE.md` for the full design and `docs/DECISIONS.md` for the reasoning behind every non-trivial choice.
