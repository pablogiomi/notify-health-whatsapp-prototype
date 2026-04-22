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
| Development environment | ⏳ In setup |
| Meta Cloud API sandbox | ⏳ Pending |
| Send endpoint | ⏸ Not started |
| Webhook receiver | ⏸ Not started |
| Database & schema | ⏸ Not started |
| Campaign runner | ⏸ Not started |
| Dashboard | ⏸ Not started |
| Deployment | ⏸ Not started |

---

## How to run it (placeholder — will be filled in as we go)

```bash
# Clone
git clone git@github.com:pablogiomi/notify-health-whatsapp-prototype.git
cd notify-health-whatsapp-prototype

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# Edit .env and fill in your Meta Cloud API credentials — see docs/setup.md

# Run
uvicorn app.main:app --reload
```

A separate `docs/setup.md` will walk through obtaining Meta Cloud API credentials and running the app end-to-end for the first time. That file does not yet exist.

---

## For the Notify Health team

If you are from Notify Health reviewing this:

- The live instance is at: *to be deployed — link coming at submission.*
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains every component and why it was chosen.
- [`docs/DECISIONS.md`](docs/DECISIONS.md) is a running log of architectural decisions — every tradeoff is documented, not hidden.
- [`docs/whatsapp-api-primer.md`](docs/whatsapp-api-primer.md) is a plain-language explanation of how the WhatsApp Cloud API actually works, useful for anyone on your team evaluating WhatsApp as a channel.
- [`docs/production-migration.md`](docs/production-migration.md) (to be added) documents what changes between this prototype and a production deployment.

---

## License

To be added. Likely MIT.
