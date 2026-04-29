# Local setup guide

Step-by-step instructions for running the prototype on your own machine.

---

## Prerequisites

| Tool | Minimum version | Notes |
|---|---|---|
| Python | 3.12 | Check with `python3 --version` |
| git | any | |
| ngrok | any | Required only for webhook testing |

Install ngrok from [ngrok.com/download](https://ngrok.com/download) or via
your package manager. You will need a free ngrok account to get a static
subdomain (optional but useful — avoids updating the webhook URL in Meta
every time you restart ngrok).

---

## 1. Clone the repository

```bash
git clone https://github.com/pablogiomi/notify-health-whatsapp-prototype.git
cd notify-health-whatsapp-prototype
```

---

## 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your prompt. All subsequent commands assume
the virtualenv is active.

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Set up a Meta developer account and app

You need a Meta developer account and a WhatsApp Business app to get the
credentials the prototype requires.

1. Go to [developers.facebook.com](https://developers.facebook.com) and
   log in with a Facebook account.
2. Click **My Apps → Create App**. Choose **Business** as the app type.
3. From the app dashboard, add the **WhatsApp** product.
4. Under **WhatsApp → API Setup**, you will find:
   - **Phone number ID** — copy this into `WHATSAPP_PHONE_NUMBER_ID` in your `.env`
   - **WhatsApp Business Account ID** — copy into `WHATSAPP_BUSINESS_ACCOUNT_ID`
   - **Temporary access token** — click **Generate token** and copy into
     `WHATSAPP_ACCESS_TOKEN`. This token expires after 24 hours; see
     the end of this guide for how to refresh it before each session.
5. Under **App Settings → Basic**, find **App Secret** and copy it into
   `WHATSAPP_APP_SECRET`.
6. Choose a webhook verify token — any string you invent, at least 20
   characters. Put it in `WHATSAPP_WEBHOOK_VERIFY_TOKEN` in your `.env`.
   You will paste the same string into Meta when registering the webhook
   URL (step 9 below).

---

## 5. Configure environment variables

Copy the example file:

```bash
cp .env.example .env
```

Fill in the values you collected in step 4. The remaining variables
(`CAMPAIGN_TEMPLATE_NAME`, `DATABASE_URL`, `LOG_LEVEL`, `PORT`) have
sensible defaults already set in `.env.example` and do not need to change
for local development.

The `.env` file is listed in `.gitignore` — it will never be committed.

---

## 6. The data/ directory

The repository includes a tracked `data/.gitkeep` file, so the `data/`
directory already exists after cloning. No manual `mkdir` is needed.
The SQLite database (`data/app.db`) is created automatically at first startup
in the `data/` directory, as configured by `DATABASE_URL` in your `.env`.

---

## 7. Seed the recipient list

The seed script reads `data/sample_recipients.csv` and inserts rows into
the `recipients` table. The database must exist first — starting the
server creates it.

```bash
# Start the server briefly to create the database, then Ctrl+C.
uvicorn app.main:app --reload

# In a second terminal (virtualenv active):
python scripts/seed_recipients.py
```

To reset to a clean state for a demo, delete `data/app.db` and re-run:

```bash
rm data/app.db
uvicorn app.main:app --reload   # recreates the schema
python scripts/seed_recipients.py
```

---

## 8. Start the development server

```bash
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`. Auto-reloads on file changes.

Useful URLs once running:

| URL | Purpose |
|---|---|
| `http://localhost:8000/dashboard` | Recipient status monitor |
| `http://localhost:8000/architecture` | System architecture diagram |
| `http://localhost:8000/health` | Liveness check |
| `http://localhost:8000/docs` | Auto-generated OpenAPI docs |

---

## 9. Set up ngrok for webhook testing

Meta needs a public HTTPS URL to deliver webhook events to your local
machine. ngrok creates an encrypted tunnel from a public URL to your
localhost.

In a separate terminal:

```bash
ngrok http 8000
```

ngrok prints a forwarding URL such as `https://abc123.ngrok-free.app`.

Then in Meta for Developers:

1. Go to your app → **WhatsApp → Configuration → Webhooks**.
2. Set **Callback URL** to `https://abc123.ngrok-free.app/webhook`.
3. Set **Verify token** to the same value you set in
   `WHATSAPP_WEBHOOK_VERIFY_TOKEN` in your `.env`.
4. Click **Verify and Save** — Meta calls `GET /webhook` to confirm
   ownership. The app echoes the challenge automatically.
5. Subscribe to the **messages** field under Webhook Fields.

Each time you restart ngrok without a static domain, the URL changes and
you must update the Callback URL in Meta. A free ngrok account lets you
reserve a static subdomain to avoid this.

---

## 10. Before each test session

The Meta temporary access token expires after 24 hours. Each time you
return to test, run through this checklist before sending any messages:

1. **Refresh the access token.** Go to Meta for Developers →
   your app → **WhatsApp → API Setup** → click **Generate token**.
   Copy the new token into `WHATSAPP_ACCESS_TOKEN` in your `.env`.

2. **Confirm the verify token is in Meta.** Go to **WhatsApp →
   Configuration → Webhooks** and check that the Verify token field
   matches `WHATSAPP_WEBHOOK_VERIFY_TOKEN` in your `.env`. This only
   needs doing once, but worth checking if webhooks are not arriving.

3. **Restart the server** so it picks up the updated `.env`:

   ```bash
   # Ctrl+C the running server, then:
   uvicorn app.main:app --reload
   ```

4. **Restart ngrok** if you stopped it. If your ngrok URL changed,
   update the **Callback URL** in Meta → WhatsApp → Configuration →
   Webhooks to the new URL.
