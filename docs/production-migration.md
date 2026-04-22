# Production migration guide

> **Status:** Placeholder. To be written on Day 6, once the prototype is deployed and we have concrete observations about what changes between sandbox and production.

This document will walk through, step by step, what Notify Health (or any successor team) needs to change to move this prototype to a real production environment sending reminders to thousands of recipients.

Expected sections:

1. Replacing the test sender phone number with a real WhatsApp Business Account number
2. Moving from a 24-hour temporary token to a long-lived System User token, with rotation procedure
3. Submitting and managing production message templates (Utility category), including localisation for recipient languages
4. Migrating from SQLite to managed Postgres
5. Applying rate limiting aligned with Meta's messaging tier
6. Opt-in management and STOP-keyword handling
7. Monitoring, alerting, and log aggregation
8. Cost estimation at expected production volumes
9. Failure playbook (webhook outages, token expiry, template rejections)

The goal of this document is that a developer unfamiliar with the project could take the prototype from sandbox to production in a single week by following it.
