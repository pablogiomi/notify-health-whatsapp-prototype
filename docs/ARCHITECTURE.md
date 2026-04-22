# Architecture

This document explains *what* the system looks like and *why* it is shaped this way. For a step-by-step log of decisions made during development, see [`DECISIONS.md`](DECISIONS.md). For a plain-language explanation of the WhatsApp Cloud API itself, see [`whatsapp-api-primer.md`](whatsapp-api-primer.md).

---

## The one-sentence version

A small web application that reads phone numbers from a database, asks WhatsApp's servers to send each a reminder message, and listens for webhook updates about whether those messages were delivered.

---

## The four actors

There are only four things in this system. Understanding these, and how they talk to each other, is understanding the whole design.

1. **The application** — Python (FastAPI) code. Runs locally during development and on Railway in production.
2. **The database** — a single SQLite file. Stores recipients, messages, and message events.
3. **Meta's WhatsApp Cloud API** — external HTTP service. Never directly visible to us; we only exchange HTTP requests with it.
4. **The recipient's phone** — runs a regular WhatsApp client.

Everything else is glue.

---

## The message lifecycle

Sending a single reminder and observing its delivery involves this sequence:

```
Application                   Meta                    Recipient's phone
     │                          │                          │
     │ 1. Read recipient row    │                          │
     │                          │                          │
     │ 2. POST /messages ──────▶│                          │
     │    (template + recipient)│                          │
     │                          │                          │
     │◀── 3. "OK, id=wamid.X" ──│                          │
     │                          │                          │
     │ Save messages row        │ 4. Routes message ──────▶│
     │ (current_status=sent)    │                          │
     │                          │◀── 5. acknowledges ──────│
     │                          │                          │
     │◀── 6. POST /webhook ─────│                          │
     │    (wamid.X, delivered)  │                          │
     │                          │                          │
     │ Insert message_events    │                          │
     │ row; update current      │                          │
     │                          │                          │
     │                          │◀── 7. user opens msg ────│
     │                          │                          │
     │◀── 8. POST /webhook ─────│                          │
     │    (wamid.X, read)       │                          │
     │                          │                          │
     │ Insert event; update     │                          │
     │                          │                          │
```

**Key property: the flow is asynchronous.** The response at step 3 is just a receipt — "I accepted your request and here's the ID." Actual delivery happens in the background and is reported via webhooks. This shape is inevitable: a phone may be off, on a plane, or on a flaky connection, and Meta cannot hold the HTTP response open until the message lands.

**Consequence:** the application must expose a public HTTP endpoint Meta can reach (the `/webhook`) and must match incoming webhooks to outbound messages by the `wamid` returned at send time.

---

## Component map

```
┌──────────────────────────────────────────────────────────┐
│                   FastAPI Application                    │
│                                                          │
│  ┌────────────┐    ┌───────────┐    ┌─────────────────┐  │
│  │  POST      │    │  POST     │    │  GET            │  │
│  │  /send     │    │  /webhook │    │  /dashboard     │  │
│  └─────┬──────┘    └─────┬─────┘    └────────┬────────┘  │
│        │                 │                   │           │
│        ▼                 ▼                   ▼           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           WhatsApp client wrapper                   │ │
│  │      (Python module around httpx + Meta API)        │ │
│  └───────────────────────┬─────────────────────────────┘ │
│                          │                               │
│  ┌───────────────────────┴─────────────────────────────┐ │
│  │           SQLAlchemy data layer                     │ │
│  │   recipients / messages / message_events            │ │
│  └───────────────────────┬─────────────────────────────┘ │
│                          │                               │
└──────────────────────────┼───────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  SQLite file  │
                   │  app.db       │
                   └───────────────┘

         External:  graph.facebook.com (Meta Cloud API)
```

### Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /send` | Trigger a campaign: iterate recipients, send each a template, record outcomes. Exposed for demo and manual runs. Internally a script could call the same code path. |
| `POST /webhook` | Receive status callbacks from Meta. Verify signature, look up message by `wamid`, append event, update message state. |
| `GET /webhook` | Webhook verification handshake. Meta calls this once when registering the endpoint; we echo the challenge to prove control of the URL. |
| `GET /dashboard` | Server-rendered HTML page showing recipients, their reachability, and the latest message status for each. Refreshes via HTMX. |
| `GET /health` | Returns `{"status":"ok"}`. Used by Railway for health checks. |

---

## Database schema

Three tables, two foreign-key relationships. Designed for clarity and straightforward migration to Postgres later.

### `recipients`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-increment |
| `phone_number` | TEXT NOT NULL UNIQUE | E.164 format (e.g. `+525512345678`) |
| `name` | TEXT | Optional display name |
| `whatsapp_reachable` | TEXT | `unknown` / `yes` / `no` |
| `last_attempted_at` | TIMESTAMP | Null until first send attempt |
| `created_at` | TIMESTAMP NOT NULL | Defaults to now |

### `messages`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-increment — our internal identifier |
| `recipient_id` | INTEGER NOT NULL | **Foreign key → recipients.id** |
| `template_name` | TEXT NOT NULL | E.g. `hello_world` |
| `template_language` | TEXT NOT NULL | E.g. `en_US` |
| `meta_message_id` | TEXT UNIQUE | The `wamid.X` Meta returns. Null until API call succeeds. Indexed for webhook lookup. |
| `current_status` | TEXT NOT NULL | Latest known: `queued` / `sent` / `delivered` / `read` / `failed` |
| `last_error_code` | INTEGER | Only set if `current_status = failed` |
| `created_at` | TIMESTAMP NOT NULL | When we called Meta's API |
| `updated_at` | TIMESTAMP NOT NULL | Updated when status changes |

### `message_events`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-increment |
| `message_id` | INTEGER NOT NULL | **Foreign key → messages.id** |
| `status` | TEXT NOT NULL | `sent` / `delivered` / `read` / `failed` / `deleted` |
| `error_code` | INTEGER | Populated on `failed` events |
| `error_message` | TEXT | Human-readable error, when available |
| `occurred_at` | TIMESTAMP NOT NULL | Timestamp from Meta's payload |
| `received_at` | TIMESTAMP NOT NULL | When *we* received the webhook |
| `raw_payload` | TEXT | JSON of the full webhook event, for debugging. Can be dropped in production. |

### Why this shape

- **Separate `messages` and `message_events`.** One message goes through multiple statuses over time (`sent` → `delivered` → `read`). Storing the latest on `messages` gives a fast dashboard query; storing every event on `message_events` preserves history for debugging and analysis. This pattern — current state plus event log — is common and robust.
- **Dual identifiers on `messages`.** We keep both our own `id` (for internal joins and primary-key stability) and Meta's `wamid` (for matching incoming webhooks). When integrating with an external service, always store their identifier as a separate indexed column.
- **`whatsapp_reachable` on `recipients`, not derived.** Reachability is expensive to re-learn (costs a send attempt), so we cache it as a column. First send attempt transitions `unknown` → `yes`/`no` based on webhook result.
- **`raw_payload` stored.** During development this is invaluable for diagnosing why something misbehaves. In production with many messages, this column would be truncated or dropped.

---

## Reachability classification

The WhatsApp Cloud API no longer exposes a reliable pre-flight "is this number on WhatsApp" check (the former `contacts` endpoint is deprecated). Reachability is therefore **treated as an observed property**, not a precondition.

The algorithm:

1. A recipient starts with `whatsapp_reachable = unknown`.
2. When a campaign sends to them, a `messages` row is created.
3. Meta's webhook will eventually return one of:
   - `delivered` or `read` → set `whatsapp_reachable = yes`.
   - `failed` with error code `131026` (message undeliverable) or `131051` (unsupported message type for recipient) → set `whatsapp_reachable = no`.
   - `failed` with other codes → leave as `unknown` (could be transient).
4. Future campaigns can choose to skip `no` recipients entirely.

This framing should appear in any write-up for Notify Health — it is the correct engineering response to a platform constraint, and framing it that way signals understanding.

---

## Technology choices

Each row links to the rationale in [`DECISIONS.md`](DECISIONS.md).

| Layer | Choice | One-line reason |
|---|---|---|
| Language | Python 3.12 | Readable; the author has prior Python exposure; widely used in global-health tooling. |
| Web framework | FastAPI | Auto-generated interactive API docs (useful for Notify Health inspection), native async for webhooks, minimal boilerplate. |
| ORM | SQLAlchemy 2.0 | Standard Python ORM; trivial switch from SQLite to Postgres. |
| Database | SQLite | Zero-setup; single file; production-credible up to thousands of msgs/day. |
| Templates | Jinja2 | Ships with FastAPI ecosystem. |
| Interactivity | HTMX (tiny) | Avoids a full JS framework for the dashboard; server renders HTML, HTMX refreshes it. |
| HTTP client | httpx | Async-capable, ergonomic. |
| Dev tunnel | ngrok | Gives `localhost` a public HTTPS URL for Meta webhooks. |
| Deployment | Railway | One-command deploy from GitHub, free tier, handles HTTPS. |
| Messaging | Meta Cloud API (test tier) | Official, free for 5 recipients, production migration is credential-swap only. |

**Explicitly rejected:** Twilio WhatsApp Sandbox (opt-in join codes make it unrepresentative of real deployment); third-party BSPs (adds an abstraction that obscures learning and later costs more); Node/TypeScript (less familiar to author); React dashboard (scope creep for an MVP).

---

## Sandbox-to-production migration

The same code runs in both environments. The following change:

| Aspect | This prototype (sandbox) | Production |
|---|---|---|
| Sender phone | Meta-provided test number | Real number owned by Notify Health, registered on a WhatsApp Business Account |
| Access token | Temporary (24-hour) dashboard token | Long-lived "System User" token, rotated on schedule |
| Recipients | ≤ 5, each manually verified in dashboard | Unlimited; opt-in managed by Notify Health's recipient-consent process |
| Template | `hello_world` (pre-approved) | Custom Utility-category template, approved by Meta (~24–72 h review) |
| Database | SQLite file on host | Managed Postgres (e.g. Railway, Supabase, RDS) |
| Hosting | Railway free tier | Notify Health's chosen cloud, with autoscaling and alerting |
| Secrets | `.env` file | Hosted secret manager (Railway vars, AWS Secrets Manager, etc.) |
| Observability | Logs in Railway dashboard | Structured logs → centralised log aggregator; metrics on send volume and failure rates; alerts on webhook failures |
| Rate limits | Well under Meta's caps | Respect Meta's messaging tiers; apply internal throttling per campaign |

**None of these requires a code rewrite.** Every item is either a configuration value, an environment variable, or an operational process layered on top. That is the architectural guarantee the prototype is designed to provide.

A full runbook-style version of this will be in `docs/production-migration.md` (to be written).

---

## Scope boundaries

What the prototype does:

- Send one template message per recipient in a campaign.
- Receive and store all status webhooks.
- Display current state in a simple dashboard.
- Classify reachability based on delivery outcomes.

What the prototype explicitly does **not** do (listed so Notify Health understands the line):

- Multi-tenancy (the system assumes one organisation is sending).
- Authentication on the dashboard (demo access only; trivial to add with FastAPI's security utilities).
- Retry logic on transient failures (noted as a production requirement).
- Scheduling of future campaigns (all sends are on-demand).
- Two-way conversation handling (inbound messages beyond status webhooks are ignored).
- Cost accounting.
- A/B testing or experiment framework.
- Recipient opt-out handling (critical for production, trivially added via an inbound-message handler).

Each of these is a well-understood next step and would be documented in the production roadmap.

---

## Non-goals for the prototype review

This prototype is deliberately *not* optimised. If reviewing the code, note the following and trust that production hardening is understood to be a separate step:

- No unit-test coverage goals beyond a handful of representative tests.
- Minimal input validation beyond what FastAPI/Pydantic provide out of the box.
- Webhook signature verification is implemented but basic.
- Error messages in the UI are functional, not polished.
- The dashboard is intentionally plain.

These are scope decisions for a time-boxed volunteer submission, not gaps in understanding.
