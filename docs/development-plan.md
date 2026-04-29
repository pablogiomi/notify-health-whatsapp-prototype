# Development Plan

## Project Overview

This project is a working WhatsApp reminder prototype built as an application exercise for Notify Health, a charity that sends immunisation reminders to caregivers in Africa. The prototype demonstrates a complete end-to-end workflow: reading recipient phone numbers from a database, sending template messages via the Meta Cloud API, receiving delivery status webhooks, classifying WhatsApp reachability, and visualising results on a dashboard. It also includes a cost-effectiveness analysis comparing WhatsApp against the current SMS/voice stack and modelling $/DALY cost-effectiveness at scale. The prototype submission deadline is **May 1, 2026**. Notify Health's full project timeline targets **September 2026** for production deployment.

---

## Completed

### Infrastructure & environment
- ✅ Dev environment (Python 3.12, virtualenv, uvicorn, ngrok)
- ✅ Railway deployment (persistent volume, environment variables, auto-deploy from main)
- ✅ `.env.example` and secrets management pattern
- ✅ `data/.gitkeep` — tracked directory for SQLite file

### Meta API integration
- ✅ Meta Cloud API sandbox verified
- ✅ Test message sent end-to-end (template → delivery → webhook → DB)

### Application
- ✅ FastAPI skeleton with startup hook and logging
- ✅ `GET /health` liveness endpoint
- ✅ `POST /send` — campaign runner; iterates recipients, sends template, records outcomes
- ✅ `GET /webhook` — Meta one-time verification handshake
- ✅ `POST /webhook` — signature-verified event handler; appends events, updates status
- ✅ Database schema and SQLAlchemy models (`recipients`, `messages`, `message_events`)
- ✅ Reachability classifier (observed from webhook error codes 131026/131051)
- ✅ Dashboard (`/dashboard`) with HTMX auto-refresh every 5s
- ✅ Architecture page (`/architecture`) — interactive SVG diagram with failure mode panel
- ✅ Cost-Effectiveness Analysis page (`/cea`) — media pricing, A/B design, $/DALY sliders, sensitivity table

### Documentation
- ✅ `docs/ARCHITECTURE.md` — component map, schema, lifecycle, migration table
- ✅ `docs/DECISIONS.md` — append-only log of every non-trivial decision (DR-001 → DR-021)
- ✅ `docs/whatsapp-api-primer.md` — plain-language explanation of the Meta API
- ✅ `docs/business-case-nigeria.md` — channel cost comparison, EPI schedule, $/DALY model
- ✅ `docs/production-migration.md` — runbook for moving from prototype to production
- ✅ `docs/backlog.md` — feature backlog and open questions for Notify Health
- ✅ `docs/setup.md` — step-by-step local setup guide

### Business case research
- ✅ Channel cost comparison (WhatsApp vs SMS vs voice, Nigeria, April 2026)
- ✅ WhatsApp penetration analysis for Nigeria and Kogi State
- ✅ Nigeria EPI schedule (7 visits; R21 malaria pending rollout)
- ✅ Notify Health scale and cost-effectiveness baseline (~5× GiveDirectly)
- ✅ Media type pricing analysis (text = audio = image = $0.014/msg)
- ✅ A/B test design (text / audio / image arms, metrics, power calculation)
- ✅ $/DALY model with sensitivity analysis (overhead multiplier × uplift)

---

## In Progress

- Nothing currently in progress.

---

## Up Next (priority order)

1. Run A/B test with real caregivers once Notify Health approves test numbers
2. Submit custom Utility template (`immunisation_reminder`) to Meta for approval
3. Add HTTP Basic Auth to dashboard before sharing with Notify Health
4. Swap SQLite for Postgres on Railway for production readiness
5. Replace `hello_world` template with approved `immunisation_reminder`
6. Final report: outcomes, delivery rates, cost per reminder, A/B test results, scalability recommendations

---

## Known Constraints & Decisions

The full decision log is in [`docs/DECISIONS.md`](DECISIONS.md). The most important constraints to keep in mind during development:

- **Test mode cap:** Meta's test tier allows at most 5 manually verified recipient numbers. All reachability classification results from test mode should not be treated as production data (see DR-014).
- **Template approval required:** No production sends can happen until a custom Utility-category template is approved by Meta. Approval takes 24–72 hours and may require wording revisions.
- **No pre-flight reachability check:** The Meta `contacts` endpoint is deprecated. Reachability is observed, not predicted — the first send attempt to a number is the only way to learn whether it is on WhatsApp (DR-002).
- **NGN/USD rate volatility:** All cost comparisons in `docs/business-case-nigeria.md` use April 2026 rates (USD/NGN ≈ 1,600). Significant naira depreciation would change the relative economics of SMS vs WhatsApp.

---

## Key Reference Numbers (April 2026)

| Metric | Value |
|---|---|
| WhatsApp Utility, Nigeria (Meta direct) | $0.014 / message |
| SMS (Africa's Talking + Telerivet) | ~$0.0085 / message |
| Voice (Africa's Talking + Telerivet) | ~$0.016 / call |
| Notify Health active caregivers | ~10,000–20,000 (2025) |
| EPI visits per child | 7 (+ 3 pending with R21 malaria) |
| WhatsApp reachability, NH caregiver base | est. 30–40% |
| NH cost-effectiveness | ~5× GiveDirectly (~$11k / death averted) |
| GiveWell 10× bar | ~$100 / DALY |
