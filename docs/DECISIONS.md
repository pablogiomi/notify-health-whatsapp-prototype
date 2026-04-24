# Design decisions log

An append-only record of every non-trivial decision made during this project. Each entry captures the context, the options considered, the choice, and the reasoning. New entries go at the bottom.

The goal of this document is to show *how* decisions are made, not just *what* was chosen. For Notify Health (and for the author's own future reference), the thinking is at least as valuable as the outcome.

---

## DR-001 — WhatsApp platform: Meta Cloud API (test tier) over Twilio Sandbox

**Date:** 2026-04-21
**Status:** Accepted

**Context.** The prototype needs to send WhatsApp messages without incurring cost and with a clear path to production. Two obvious options: Meta's own Cloud API (test tier) and Twilio's WhatsApp Sandbox.

**Options considered.**

- **Meta Cloud API test tier.** Free test phone number, pre-approved `hello_world` template, up to 5 verified recipients, real Meta infrastructure, standard webhooks. Migration to production is credential swap + template approval + verified business number.
- **Twilio WhatsApp Sandbox.** Recipients must send a magic "join" phrase to a shared Twilio sandbox number before the sender can message them. Good for quick experimentation; unrepresentative of how production WhatsApp outreach actually works (recipients in production do not opt in via keywords).
- **A third-party BSP** (360dialog, MessageBird, etc.). Adds another abstraction layer and another vendor relationship. Unnecessary for this scope.

**Decision.** Meta Cloud API, test tier.

**Reasoning.** Closer to production reality (Notify Health will most likely use Meta directly or via a BSP-of-Meta anyway), no recipient opt-in theatre in the demo, and the migration story is cleaner. The 5-recipient cap is the only limitation and it is enough for a credible demo.

---

## DR-002 — Reachability classification: observed, not pre-flight

**Date:** 2026-04-21
**Status:** Accepted

**Context.** The brief asks the system to "determine whether a phone number can receive WhatsApp messages." Meta deprecated the `contacts` endpoint that used to answer this directly.

**Options considered.**

- **Build a heuristic pre-check** (e.g. phone-number formatting validation, country-code sanity). Only catches the most obvious errors.
- **Attempt-and-observe:** send a template; infer reachability from webhook outcomes (`delivered`/`read` = yes; `failed` with specific codes = no).
- **Use a paid third-party "WhatsApp validation" service.** Costs money; often produces false positives; not aligned with "no cost to evaluate."

**Decision.** Attempt-and-observe. Each recipient starts with `whatsapp_reachable = unknown`. The first send attempt transitions it based on webhook feedback. Future campaigns can skip known-unreachable numbers.

**Reasoning.** This is how mature messaging systems actually work. Framing the requirement this way demonstrates understanding of the platform's real constraints, not just the letter of the ask.

---

## DR-003 — Language: Python over Node/TypeScript

**Date:** 2026-04-21
**Status:** Accepted

**Context.** Either language can do the job. The choice affects learning curve, library ecosystem, and the author's ability to explain the code in an interview.

**Decision.** Python 3.12.

**Reasoning.** Author has prior Python exposure from college. Global-health and NGO tech spaces tilt heavily Python (historical inertia from data science, scripting, and Django). Async in Python is mature enough for this workload. No strong type-safety argument for TypeScript at this scale.

---

## DR-004 — Web framework: FastAPI

**Date:** 2026-04-21
**Status:** Accepted

**Context.** Within Python, the serious options are FastAPI, Flask, and Django.

**Decision.** FastAPI.

**Reasoning.** Three reasons:

1. **Auto-generated OpenAPI docs at `/docs`.** For Notify Health inspecting the project, being able to open a URL and interactively test the API is a large win for zero effort.
2. **Pydantic validation.** Incoming webhook payloads are parsed into typed models rather than raw dictionaries, reducing a category of bugs.
3. **Async-native.** Webhooks and outbound HTTP to Meta are I/O-bound; async is the right tool. Flask would require workarounds.

Django was considered and rejected — too much framework for what is essentially three endpoints and a dashboard. Flask was considered and rejected — FastAPI does everything Flask does, plus the above, with no meaningful downside.

---

## DR-005 — Database: SQLite for the prototype

**Date:** 2026-04-21
**Status:** Accepted

**Context.** The prototype needs persistent storage for recipients, messages, and events. Options range from "a CSV file" (too limited) to "managed Postgres" (overkill).

**Decision.** SQLite, accessed via SQLAlchemy 2.0.

**Reasoning.** Single file; zero deployment complexity; free; supports everything we need (indexes, foreign keys, transactions). Via SQLAlchemy, swapping to Postgres in production is a one-line connection-string change. Up to a few thousand messages a day, SQLite is genuinely production-grade — it is not just a toy.

**Trade-off acknowledged.** Writes are single-writer; high concurrency would be a problem at real scale. Noted as a production migration item.

---

## DR-006 — ORM vs. raw SQL

**Date:** 2026-04-21
**Status:** Accepted

**Context.** An ORM (Object-Relational Mapper) adds a layer between Python and the database. It is convenient but adds complexity.

**Decision.** Use SQLAlchemy 2.0 as an ORM.

**Reasoning.** The schema is small enough that raw SQL would work, but the ORM earns its keep here:

- Model classes double as documentation of the schema.
- Migrations (via Alembic, if needed later) become tractable.
- Swapping SQLite for Postgres requires changing one string instead of auditing every query for dialect differences.

The cost — a learning curve for an ORM-new developer — is real but worth paying for a project intended to evolve.

---

## DR-007 — Dashboard: HTMX over a JS framework

**Date:** 2026-04-21
**Status:** Accepted

**Context.** The dashboard needs to show live-ish message status. Options: a React/Vue/Svelte SPA, vanilla JavaScript with `fetch`, or a server-rendered page with HTMX.

**Decision.** Server-rendered Jinja2 templates with a sprinkle of HTMX for refresh.

**Reasoning.**

- A React SPA would consume one to two days of project time that is better spent on the core flow and documentation.
- HTMX lets the server return HTML fragments that replace parts of the page. This is plenty for "refresh the status column every 5 seconds."
- For Notify Health to read and understand the code, a simple server-rendered app is dramatically easier than a separate frontend build.

**Trade-off acknowledged.** Not a modern reactive UX. That is fine for a prototype dashboard viewed by a handful of people.

---

## DR-008 — Hosting: Railway

**Date:** 2026-04-21
**Status:** Accepted

**Context.** Need a public HTTPS URL (required for Meta webhooks), free tier, deploy from GitHub, minimal operational overhead.

**Options considered.** Railway, Render, Fly.io, Vercel (not a good fit for Python+SQLite), self-hosted VPS.

**Decision.** Railway.

**Reasoning.** Free tier is sufficient, deploys from GitHub on push, persistent disk supported (needed for the SQLite file), HTTPS is automatic, environment variables are first-class. Render is a close second and would be a fine alternative.

**Trade-off acknowledged.** Free tier may sleep or have resource limits that become annoying. Upgrade is cheap if needed.

---

## DR-009 — Secrets handling: .env file + environment variables

**Date:** 2026-04-21
**Status:** Accepted

**Context.** The app needs Meta credentials (access token, phone number ID, webhook verify token, app secret). These must never be committed to Git.

**Decision.** Local development uses a `.env` file, loaded by `python-dotenv`. `.env` is listed in `.gitignore`. A committed `.env.example` documents what variables are needed without their values. Production uses Railway's environment variable configuration.

**Reasoning.** Standard Twelve-Factor App practice. Separates configuration from code. Makes the same code run in development, staging, and production without modification.

---

## DR-010 — Webhook signature verification: required, even in the prototype

**Date:** 2026-04-21
**Status:** Accepted

**Context.** Meta signs webhook payloads with an HMAC using the app secret. Verifying this signature prevents spoofed callbacks. It would be technically possible to skip verification in a prototype.

**Decision.** Verify the `X-Hub-Signature-256` header on every `POST /webhook`. Reject on mismatch.

**Reasoning.** Once the app is deployed to a public URL, anyone can POST anything to `/webhook`. Without verification, a bad actor could send fake "delivered" events that corrupt the data. The implementation is ~10 lines of code. No reason to omit it, and including it signals understanding of basic web security.

---

## DR-011 — Storage of raw webhook payloads

**Date:** 2026-04-21
**Status:** Accepted

**Context.** Each webhook event from Meta contains a structured payload. We extract the fields we care about. Should we also keep the full original?

**Decision.** Yes — store the raw JSON in a `raw_payload` column on `message_events`. Flag for removal in production once monitoring is mature.

**Reasoning.** In development, 90% of mysterious bugs trace back to "what exactly did Meta send us?" Having the raw payload turns debugging sessions into five-minute lookups. At production scale the column becomes expensive and the need diminishes — hence the explicit plan to drop it.

---

## DR-012 — Deployment trigger: push to `main`

**Date:** 2026-04-21
**Status:** Accepted

**Context.** Railway can auto-deploy on Git push. We could alternatively require manual deploys.

**Decision.** Auto-deploy on push to `main`. Use feature branches + PR merges for anything non-trivial.

**Reasoning.** For a solo prototype on a tight deadline, the friction of manual deploys is not worth the safety. The branch discipline (work on `feat/x`, merge to `main` when green) is enough guardrail.

---

## DR-013 — Running log vs. final document

**Date:** 2026-04-21
**Status:** Accepted

**Context.** Should architectural reasoning be written up once at the end, or continuously as we work?

**Decision.** Continuously, here, as we go. The final `ARCHITECTURE.md` is derived from this log, not written separately.

**Reasoning.** Reasoning written after the fact is reliably cleaner, more coherent, and less true. A running log captures the actual tradeoffs at the moment they were real, which is much more useful for the reader trying to understand how this system came to be. For Notify Health, the log itself is evidence of the engineering process, not just the outcome.

---

## DR-014 — Test-mode failure codes differ from production

**Date:** 2026-04-24
**Status:** Observed during development

**Context.** In Meta's test tier, sending to an unverified recipient number returns a send-level failure (HTTP 4xx, no wamid assigned) rather than a webhook-level failure (wamid assigned, later failed webhook with error code 131026).

**Consequence.** The reachability classifier (DR-002) only triggers on webhook-level failures carrying error codes 131026 or 131051. Send-level failures leave whatsapp_reachable = "unknown" because we cannot distinguish "number not on WhatsApp" from "number not verified in test mode."

**In production.** All numbers are reachable for send attempts. A number that isn't on WhatsApp will receive a wamid, then fail with error code 131026 in a webhook callback, correctly triggering the classifier.

**Implication for Notify Health.** The reachability classification feature works correctly in production. Test-mode results for unverified numbers should not be interpreted as reachability data.

---

## DR-015 — Graph API version: pinned to v25.0

**Date:** 2026-04-22
**Status:** Accepted

**Context.** Meta's Graph API releases new versions regularly and eventually deprecates old ones. The default version in Meta's own code snippets was v23.0 at project start; the live API was already running v25.0 as observed in response headers during Day 1 testing.

**Decision.** Pin explicitly to v25.0 in config.py default and CLAUDE.md. Bump intentionally when Meta announces deprecations.

**Reasoning.** Unpinned version references mean Meta upgrades can silently change behaviour. A pinned version makes upgrades a deliberate decision with a visible diff. Observed during Day 1 when the curl smoke test response headers showed facebook-api-version: v25.0 while our config said v23.0.

---

## DR-016 — Template language: en_US for prototype only

**Date:** 2026-04-22
**Status:** Accepted

**Context.** The hello_world test template ships with Meta test accounts in en_US only. Notify Health's production use case involves multiple languages (English, Swahili, French, and others depending on country of deployment).

**Decision.** Hard-code en_US as the default in config for the prototype. Treat multi-language support as a production concern.

**Reasoning.** Template localisation requires separate Meta approval per language per template — a process that cannot be completed within the prototype timeline. The architecture supports multiple languages (template_language is a config value, not hardcoded in logic), so adding languages later is an operational process, not a code change. Flagged in production-migration.md.

---

## DR-017 — Railway persistent volume mount path

**Date:** 2026-04-24
**Status:** Accepted

**Context.** Railway's ephemeral filesystem resets on every deploy.
SQLite requires a persistent volume to survive redeployments.

**Decision.** Mount volume at /app/data, set
DATABASE_URL=sqlite:////app/data/app.db (absolute path,
four slashes).

**Reasoning.** Mounting at /app would conflict with application
files. /app/data is a clean subdirectory. Four slashes in the
SQLAlchemy URL denotes an absolute path from filesystem root —
three slashes would be relative to the working directory and
would write to the ephemeral filesystem instead.

**Observed failure mode.** Environment variables were wiped after
a force-push history rewrite (git filter-repo). Railway treated
the rewritten history as a new deployment context. Recovery:
re-enter all variables from local .env file.

---

## DR-018 — Dashboard PII protection: masked phone numbers

**Date:** 2026-04-24
**Status:** Accepted

**Context.** The dashboard is publicly accessible (no auth) and
displays recipient phone numbers. Anyone with the Railway URL
can see them.

**Decision.** Mask phone numbers on the dashboard, showing only
the last 4 digits (e.g. "···8089").

**Reasoning.** Full phone numbers are PII. The dashboard is
a demo tool, not a data management interface — last 4 digits
are sufficient to identify a recipient during a demo. Full
authentication on the dashboard is the correct production
solution (documented in production-migration.md) but out of
scope for the prototype.

---

*New decisions will be added below as they occur.*
