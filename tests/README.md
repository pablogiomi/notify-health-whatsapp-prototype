# tests/ — Automated tests

Pytest-based tests live here. Empty on Day 1; tests are added alongside the code from Day 2 onward.

Plan:

- `test_webhooks.py` — verify signature validation and event dispatch
- `test_whatsapp_client.py` — mocked tests of the Meta API wrapper
- `test_campaigns.py` — end-to-end dry-run of a campaign against a mocked Meta client
- `test_models.py` — sanity checks on the data layer

Run with:

```bash
pytest
```
