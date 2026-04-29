# notify-health-whatsapp-prototype

> A working prototype exploring WhatsApp as a delivery channel for immunisation reminder messages, built as an application exercise for [Notify Health](https://www.notifyhealth.org/).

**Status:** In development. Target completion: May 1, 2026.

**Author:** Pepigiomi ([@pablogiomi](https://github.com/pablogiomi))

---

## What this is

Notify Health is a charity that sends SMS immunisation reminders to caregivers in Africa. They are exploring whether WhatsApp could be a complementary or replacement channel — potentially reaching tens of thousands more children and saving over $100,000 per year in digitisation costs.

This prototype demonstrates a complete, end-to-end WhatsApp reminder workflow:

1. **Read** recipient phone numbers from a database.
2. **Classify** whether each number is reachable on WhatsApp (inferred from delivery attempts; the WhatsApp platform does not expose a reliable pre-flight check).
3. **Send** reminder messages via pre-approved templates using the WhatsApp Cloud API.
4. **Monitor** delivery status (`sent` / `delivered` / `read` / `failed`) through webhook callbacks.
5. **Visualise** results on a small dashboard.

Everything runs on the free Meta Cloud API test tier and free hosting — no recurring cost to evaluate.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the design and [`docs/DECISIONS.md`](docs/DECISIONS.md) for the reasoning behind every meaningful choice.

---

## Current state

This README will be updated as the project progresses. At any point it reflects what actually works, not what is planned.

| Area | Status |
|---|---|
| Development environment | ✅ Ready |
| Meta Cloud API sandbox | ✅ Verified (test message sent end-to-end) |
| FastAPI skeleton  | ✅ Running (health endpoint verified) |
| Send endpoint           | ✅ Working                                     |
| Webhook receiver        | ✅ Working (signature verified, events logged) |
| Database & schema       | ✅ Working                                     |
| Campaign runner         | ✅ Working                                     |
| Dashboard               | ✅ Working (HTMX auto-refresh)                 |
| Deployment              | ✅ Live on Railway                             |
| Cost-Effectiveness Analysis (/cea) | ✅ Live on Railway |

---

## How to run it

See [`docs/setup.md`](docs/setup.md) for the full step-by-step guide covering prerequisites, virtual environment setup, Meta developer account configuration, seeding recipients, starting the server, and setting up ngrok for local webhook testing.

---

## For the Notify Health team

If you are from Notify Health reviewing this:

- The live instance is at: (https://web-production-25be6.up.railway.app/dashboard)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains every component and why it was chosen.
- [`docs/DECISIONS.md`](docs/DECISIONS.md) is a running log of architectural decisions — every tradeoff is documented, not hidden.
- [`docs/whatsapp-api-primer.md`](docs/whatsapp-api-primer.md) is a plain-language explanation of how the WhatsApp Cloud API actually works, useful for anyone on your team evaluating WhatsApp as a channel.
- [`docs/production-migration.md`](docs/production-migration.md) (to be added) documents what changes between this prototype and a production deployment.

---

## Business Case

A cost analysis comparing WhatsApp, SMS, and voice channels for immunisation
reminders in Nigeria is documented in
[`docs/business-case-nigeria.md`](docs/business-case-nigeria.md).

Key findings (April 2026):
- WhatsApp utility: $0.014/msg (Nigeria, Meta direct API)
- SMS via Africa's Talking + Telerivet: ~$0.0085/msg
- Voice via Africa's Talking + Telerivet: ~$0.016/call
- No price difference between text, image, and audio templates
- Current Notify Health cost-effectiveness: ~5× GiveDirectly
- A/B test (text vs audio vs image) is the primary lever for
  improving $/DALY without increasing per-message cost

---

## License

To be added. Likely MIT.
