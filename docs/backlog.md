# Backlog

Features and open questions that are not required to stand up a
production deployment but must be resolved before the system is
considered complete. Items marked **compliance-critical** carry
legal or Meta policy risk if skipped.

---

## 1. Recipient opt-in confirmation _(compliance-critical)_

**Status:** Not implemented.

Meta requires that recipients have actively opted in to receive
WhatsApp messages before a business can contact them. The current
prototype assumes consent exists but does not record or verify it.
Before production:

- Capture the opt-in event (timestamp, channel, wording shown)
  and store it against each recipient
- Ensure the opt-in record is producible on request — Meta may
  ask for evidence during account quality reviews
- Align with Notify Health's existing consent process to avoid
  collecting consent twice, but confirm it covers WhatsApp
  specifically (SMS consent does not automatically extend)

Failure to demonstrate opt-in is grounds for template rejection
and account suspension.

## 2. Recipient opt-out handling _(compliance-critical)_

**Status:** Not implemented.

When a recipient replies STOP, Meta fires an inbound message
webhook. Add a handler in `webhook.py` that:

- Parses the inbound message type from the webhook payload
- Matches the sender's phone number to a `Recipient` row
- Sets `whatsapp_reachable = "no"` and logs the event

Required for legal compliance (consent withdrawal) and Meta's
spam policies. Failure to handle opt-outs risks account suspension.

## 3. Retry logic

**Status:** Not implemented. Failed sends are logged and skipped.

Implement exponential backoff for transient failures:

- Retry on network errors and HTTP 429 (rate limit)
- Do **not** retry on permanent error codes 131026 or 131051
  (these indicate the number is unreachable — retrying wastes
  quota and may degrade account quality score)

## 4. Audio messages, voice calls, and A/B testing

**Status:** Not implemented. Current reminders are text-only.

WhatsApp supports audio message templates and, via Meta's
Business Calling API, outbound voice calls. Notify Health may
see higher recall rates if reminders are delivered as audio
rather than text — recipients in low-literacy contexts are more
likely to act on a voice reminder than a written one.

Proposed experiment:

- Implement an audio template variant (pre-recorded or
  text-to-speech) sent alongside or instead of the text template
- Add a campaign-level `variant` field (`text` / `audio` /
  `call`) so recipients can be split across delivery channels
- Track read/played status from webhook events — Meta reports
  `read` for audio messages when the recipient plays them
- Compare recall rate (vaccination attendance, if Notify Health
  can supply outcome data) across variants

Questions to resolve before scoping:
- Does Notify Health have access to Meta's Business Calling API
  (separate approval from standard Cloud API)?
- Who records or generates the audio content, and in which
  languages?
- What is the outcome metric — attendance records, self-report,
  or something else?

## 5. Inbound messages beyond STOP

**Status:** Not implemented.

Recipients may reply with messages other than STOP. Currently
these arrive via webhook and are silently ignored. Options:

- Log all inbound messages to `message_events` for audit purposes
- Forward to a human inbox (email or Slack notification)
- Auto-reply with a "this number does not receive messages"
  notice to manage expectations

No priority assigned — confirm with Notify Health whether
recipients are expected to reply at all.

## 6. Multi-tenancy

**Status:** Not designed.

The current data model assumes a single organisation. Supporting
multiple organisations would require:

- A `tenants` table with per-tenant Meta credentials
- Foreign keys from `recipients` and `messages` to `tenants`
- Per-tenant isolation in all queries
- Credential routing in `whatsapp.py`

This is an architectural change — raise before any production
deployment that serves more than one organisation.

## 7. `raw_payload` removal

**Status:** Stored in `message_events.raw_payload`; flagged as a
drop-candidate.

The full Meta webhook JSON is kept during development for
debugging. Before production:

- Confirm no downstream tooling depends on it
- Add a migration to drop the column (or null it out for existing
  rows if column removal is disruptive)
- Update `webhook.py` to stop writing it

## 8. Open questions

- **Alembic:** The app currently calls `create_all` at startup.
  Before any schema change in production, migrate to Alembic
  so that schema changes are versioned and reversible.

- **Campaign scheduling:** Campaigns are triggered manually via
  `POST /send`. Notify Health will likely need time-scheduled
  sends (e.g., run at 08:00 local time). Decide whether to
  implement a scheduler (APScheduler, Celery, or Railway cron)
  or rely on an external trigger.

---

## 9. Questions for Notify Health

Answers needed before finalising the production architecture.

### Telerivet integration

- How is Notify Health currently using Telerivet — push or pull
  for recipient lists?
- Does Telerivet own the source of truth for recipients, or is
  there a separate patient/contact database?
- Should this system eventually replace Telerivet, run alongside
  it, or receive data from it?

### Hosting

- Does Notify Health have an existing cloud provider or
  infrastructure preference (AWS, GCP, Azure, on-prem)?
- Are there data-residency or compliance constraints that
  restrict where recipient data can be stored?

### Dashboard authentication

- Does Notify Health have an existing identity provider
  (Google Workspace, Azure AD, Okta) that a login should
  integrate with?
- If not, is HTTP Basic Auth acceptable as a short-term
  measure, or is a full login flow required before launch?

### Template languages

- Which languages are needed at launch?
- Does Notify Health already have approved translations, or
  will new copy need to be written and submitted to Meta?
- Are templates expected to vary by region/country, or is one
  template per language sufficient?
