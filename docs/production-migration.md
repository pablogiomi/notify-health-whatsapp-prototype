# Production migration guide

This document describes what changes between this prototype
and a production deployment. Every item is a configuration
change, credential swap, or operational process — no code
rewrites are required.

## 1. Sender phone number

**Prototype:** Meta-provided test number shared across all
developer accounts.
**Production:** A real phone number owned by Notify Health,
registered on a verified WhatsApp Business Account.
Registration requires Meta business verification (~1-5 days).

## 2. Access token

**Prototype:** Temporary 24-hour token generated from the
Meta developer dashboard.
**Production:** A long-lived System User token that does not
expire. Created via Meta Business Manager → System Users →
Generate Token. Rotate on a schedule (every 6-12 months)
and store in a secrets manager rather than plain environment
variables.

## 3. Recipients

**Prototype:** Up to 5 manually verified numbers in test mode.
**Production:** Unlimited. Recipients do not need to opt in
via any Meta process — they receive messages as long as a
valid template is used. Notify Health's existing consent
process (used for SMS) applies.

## 4. Message template

**Prototype:** hello_world (pre-approved, ships with all
test accounts, English only).
**Production:** Custom Utility-category template submitted
to Meta for approval. Approval takes 24-72 hours and may
require wording changes. One submission per language —
submit all required languages before launch.

Suggested template for Notify Health:

    Category: Utility
    Name: immunisation_reminder
    Body: "Hi {{1}}, this is a reminder that {{2}} is due for
    their {{3}} vaccination on {{4}}. Reply STOP to opt out."

## 5. Database

**Prototype:** SQLite file on Railway's persistent volume.
**Production:** Managed Postgres (Railway, Supabase, or AWS
RDS). Migration is a one-line change to DATABASE_URL —
SQLAlchemy abstracts the dialect. Run Alembic migrations
instead of create_all at startup.

## 6. Dashboard authentication

**Prototype:** No authentication — dashboard is publicly
accessible.
**Production:** Add HTTP Basic Auth or OAuth2 via FastAPI's
security utilities. Required before any real recipient data
is loaded. Estimated effort: 2-4 hours.

## 7. Hosting

**Prototype:** Railway free tier — may sleep, limited
resources, no SLA.
**Production:** Railway Hobby/Pro tier, or Notify Health's
preferred cloud provider. Enable autoscaling if campaign
volumes exceed 1,000 messages/day.

## 8. Secrets management

**Prototype:** Railway environment variables (encrypted at
rest, sufficient for a prototype).
**Production:** Dedicated secrets manager — AWS Secrets
Manager, HashiCorp Vault, or Railway's secret references.
Enables rotation, auditing, and fine-grained access control.

## 9. Observability

**Prototype:** Logs visible in Railway dashboard.
**Production:** Structured logs forwarded to a centralised
aggregator (Datadog, Papertrail, or similar). Alerts on:
- Webhook failure rate > 5%
- Campaign send failure rate > 10%
- Access token expiry (proactive alert 48h before expiry)
- Database disk usage > 80%

## 10. Rate limiting

**Prototype:** Well under Meta's messaging tier limits.
**Production:** Respect Meta's tiered limits (1,000 →
10,000 → 100,000 messages/day based on account quality
score). Apply internal throttling in campaigns.py to
stay within limits during large campaigns.

## 11. Recipient opt-out handling

**Prototype:** Not implemented.
**Production:** When a recipient replies STOP, an inbound
message webhook fires. Add a handler in webhook.py that
sets whatsapp_reachable = "no" and logs the opt-out.
Critical for legal compliance and Meta's spam policies.

## 12. Retry logic

**Prototype:** Failed sends are logged and skipped.
**Production:** Implement exponential backoff retry for
transient failures (network errors, 429 rate limits).
Do not retry permanent failures (131026, 131051).

## Migration checklist

- [ ] Meta business verification complete
- [ ] Real sender number registered and approved
- [ ] System User token generated and stored
- [ ] Custom template submitted and approved (all languages)
- [ ] Postgres database provisioned and DATABASE_URL updated
- [ ] Dashboard authentication added
- [ ] All environment variables migrated to secrets manager
- [ ] Observability pipeline configured
- [ ] Rate limiting tested at expected campaign volume
- [ ] Opt-out handler implemented and tested
- [ ] Load test at 10% of expected peak volume
