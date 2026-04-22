# Day 1 checklist (2026-04-22)

A copy-pasteable walkthrough of everything to do tomorrow. Each section is self-contained.

**Total expected time:** 3–5 hours, depending on depth of reading and how smooth the Meta signup goes.

---

## Before you start

Open three browser tabs:

- [https://github.com](https://github.com) (logged in to your account `pablogiomi`)
- [https://developers.facebook.com](https://developers.facebook.com) (log in with your personal Facebook account)
- [https://railway.app](https://railway.app) (no account yet — you will create one)

Open one Ubuntu terminal (from Start menu or by typing `ubuntu` in PowerShell then pressing Enter).

---

## Part A — Verify yesterday's setup is still good

```bash
git --version
python3 --version
pip3 --version
curl --version
```

All four should print versions. If any is missing, reinstall with:

```bash
sudo apt update && sudo apt install -y git python3 python3-pip python3-venv curl
```

---

## Part B — Configure Git identity

First get your GitHub "noreply" email:

1. [github.com](https://github.com) → avatar (top right) → **Settings** → **Emails** (left sidebar).
2. Turn on **"Keep my email addresses private"**.
3. Copy the `NNNNNNNN+pablogiomi@users.noreply.github.com` address shown below.

Then in Ubuntu:

```bash
git config --global user.name "Pepigiomi"
git config --global user.email "REPLACE_WITH_YOUR_NOREPLY_EMAIL"
git config --global init.defaultBranch main
```

Verify:

```bash
git config --global user.name
git config --global user.email
```

Both should echo back what you set.

---

## Part C — Generate an SSH key and connect GitHub

```bash
ssh-keygen -t ed25519 -C "REPLACE_WITH_YOUR_NOREPLY_EMAIL"
```

At all three prompts, press Enter to accept defaults. No passphrase.

Then:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

The last command prints your public key — one long line starting `ssh-ed25519 AAAA...`. Select the whole line and copy it.

Add it to GitHub:

1. [github.com](https://github.com) → avatar → **Settings** → **SSH and GPG keys** → **New SSH key**.
2. Title: `Pepibook WSL Ubuntu`. Key type: Authentication. Paste the key. **Add SSH key**.

Verify from Ubuntu:

```bash
ssh -T git@github.com
```

Type `yes` when prompted about authenticity. You should end with:

> `Hi pablogiomi! You've successfully authenticated, but GitHub does not provide shell access.`

That's the success message.

---

## Part D — Create the repository and pull our documentation

In Ubuntu:

```bash
mkdir -p ~/code
cd ~/code
```

Create the repo on GitHub:

1. [github.com](https://github.com) → green **New** button (top left).
2. Owner: `pablogiomi`. Name: `notify-health-whatsapp-prototype`. Description: *"Prototype: WhatsApp as a channel for immunisation reminder messages — built for Notify Health."*
3. Public. Do **not** initialise with a README (we have our own). Click **Create repository**.

Back in Ubuntu:

```bash
cd ~/code
git clone git@github.com:pablogiomi/notify-health-whatsapp-prototype.git
cd notify-health-whatsapp-prototype
```

Now populate the repo with the documents Claude prepared. You should have received these files as a download bundle — copy all of them into `~/code/notify-health-whatsapp-prototype/` preserving the folder structure. On WSL you can copy from a Windows Downloads folder like this:

```bash
# If the files are in Windows Downloads, they're accessible here:
ls /mnt/c/Users/YOUR_WINDOWS_USERNAME/Downloads/

# Copy the bundle — adjust the path to match where you saved it:
cp -r /mnt/c/Users/YOUR_WINDOWS_USERNAME/Downloads/project/* .
cp -r /mnt/c/Users/YOUR_WINDOWS_USERNAME/Downloads/project/.* . 2>/dev/null || true
```

Verify:

```bash
ls -la
ls docs/
```

You should see `README.md`, `.gitignore`, `.env.example`, and `docs/` containing `ARCHITECTURE.md`, `DECISIONS.md`, `whatsapp-api-primer.md`, and this checklist.

First commit:

```bash
git add .
git status                  # review what will be committed
git commit -m "Initial project documentation and scaffolding"
git push -u origin main
```

Refresh your GitHub repo page — the files should appear. Congratulations, you have a public GitHub repo with documentation that already looks professional.

---

## Part E — Meta Developer account and WhatsApp test app

This is the longest section. Allow 45–60 minutes.

### E.1 — Create a developer account

1. Go to [developers.facebook.com](https://developers.facebook.com). Click **Get Started**. Log in with your personal Facebook.
2. Complete the short developer registration (name, email, purpose).
3. Go to **My Apps** → **Create App**.
4. Use case: select **Other** → **Next**. App type: **Business** → **Next**.
5. App name: `Notify Health WhatsApp Prototype`. Contact email: your own. Business portfolio: if you don't have one, Meta will create one automatically. Click **Create app**.

### E.2 — Add WhatsApp product

1. In your new app's dashboard, find the **Add products** section.
2. Scroll to **WhatsApp** → **Set up**.
3. This creates (automatically):
   - A test WhatsApp Business Account
   - A test business phone number
   - A pre-approved `hello_world` template
4. You land on the **API Setup** page. **Do not close this tab** — you will copy values from it.

### E.3 — Capture the important values

On the API Setup page, find and copy into a safe note (you'll put these in `.env` next):

- **Temporary access token.** Green "Generate access token" or similar. Expires in 24 hours, don't worry about that.
- **Phone number ID.** A long integer under the test sender number. Labelled "Phone number ID."
- **WhatsApp Business Account ID** (also called WABA ID).
- **App secret.** This is in the app's main **Settings → Basic** page, not the WhatsApp page. Click "Show" next to App Secret; you may have to enter your Facebook password.

You will also invent a `WEBHOOK_VERIFY_TOKEN` — any random string at least 20 characters. Make one up and write it down. You will give this same string to Meta when you register the webhook later.

### E.4 — Add yourself as a verified recipient

Still on API Setup:

1. In the "Send and receive messages" section, find the **To** field.
2. **Manage phone number list** → add your personal WhatsApp number (the one you normally use).
3. Meta sends a 6-digit code via WhatsApp. Enter it to verify.
4. Your number is now an allowed test recipient.

### E.5 — Send your first real message, by hand

From the API Setup page, copy the pre-filled cURL command and paste it into your Ubuntu terminal. It will look roughly like:

```bash
curl 'https://graph.facebook.com/v23.0/YOUR_PHONE_NUMBER_ID/messages' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{ "messaging_product": "whatsapp", "to": "YOUR_PHONE", "type": "template", "template": { "name": "hello_world", "language": { "code": "en_US" } } }'
```

Press Enter.

If everything is correctly set up, your personal phone should receive a WhatsApp message from Meta within seconds saying something like "Hello World".

**This is the milestone of Day 1.** Every other thing you build from now on is variations on what you just did.

If you get an error, paste the full response into our next chat session and we'll diagnose.

---

## Part F — Install Node.js (needed for Claude Code)

Claude Code is distributed via npm, so we need Node.js first. The safest way on Ubuntu is via `nvm` (Node Version Manager):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

Close and reopen your Ubuntu terminal. Then:

```bash
nvm install --lts
nvm use --lts
node --version
npm --version
```

Both should print versions.

---

## Part G — Install and log in to Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Then:

```bash
cd ~/code/notify-health-whatsapp-prototype
claude
```

First run, it will prompt you to log in. Follow the browser flow with your Claude Pro account.

**Important:** if asked whether to use API credits, say no — we want to use your Pro plan allocation.

When logged in, try a test prompt: `what is in the docs folder of this project?` Claude Code should read the files and summarise them. If yes, you're done.

---

## Part H — Create ngrok account and install

1. [ngrok.com](https://ngrok.com) → sign up (free).
2. After signup, you'll land on a "Getting Started" page. Copy the **authtoken** shown there.

Install ngrok in Ubuntu:

```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
    && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list \
    && sudo apt update \
    && sudo apt install ngrok
```

Authenticate:

```bash
ngrok config add-authtoken PASTE_YOUR_AUTHTOKEN_HERE
```

Test it (we're not going to use the tunnel yet, just verify it works):

```bash
ngrok http 8000
```

You'll see a UI with a `https://xxxx.ngrok-free.app` URL. Press Ctrl+C to stop it. That URL is what we'll give Meta on Day 2 as the webhook endpoint.

---

## Part I — Create a Railway account

1. [railway.app](https://railway.app) → sign up (use "Continue with GitHub" — simplest).
2. Authorise Railway to access your GitHub repos.
3. You don't need to deploy anything today. Just having the account is enough.

---

## Part J — Final Day 1 commit

Update the README status table to reflect progress. Back in Ubuntu:

```bash
cd ~/code/notify-health-whatsapp-prototype
```

Open `README.md` in a text editor (e.g. `nano README.md` in the terminal, or use VS Code with the WSL extension — see below). Change:

```
| Development environment | ⏳ In setup |
| Meta Cloud API sandbox  | ⏳ Pending  |
```

to:

```
| Development environment | ✅ Ready    |
| Meta Cloud API sandbox  | ✅ Verified (test message sent end-to-end) |
```

Save. Then:

```bash
git add README.md
git commit -m "Day 1 complete: dev env + Meta sandbox verified end-to-end"
git push
```

Refresh GitHub — the commit and status update are there.

---

## Bonus: install VS Code with the WSL extension

Not strictly required for Day 1, but makes Day 2 much nicer.

1. Install VS Code on **Windows** from [code.visualstudio.com](https://code.visualstudio.com).
2. Open VS Code. Extensions panel (left sidebar, four-squares icon). Search "WSL". Install the Microsoft-published "WSL" extension.
3. In Ubuntu terminal: `cd ~/code/notify-health-whatsapp-prototype && code .` — if everything is set up, VS Code opens connected to your WSL environment with the project already loaded.

---

## What you've achieved by end of Day 1

- Fully working Linux development environment on Windows.
- GitHub repo at [github.com/pablogiomi/notify-health-whatsapp-prototype](https://github.com/pablogiomi/notify-health-whatsapp-prototype) with professional documentation already in place.
- Meta developer account, test WhatsApp number, access token — all the credentials we need.
- A real WhatsApp message, sent from your terminal to your phone, via code.
- Claude Code, ngrok, and Railway set up and waiting for Day 2.

**Day 2 will focus on:** FastAPI skeleton, the `/send` endpoint, the `/webhook` endpoint, wiring it all together with ngrok so the first round trip works in code (not just cURL).
