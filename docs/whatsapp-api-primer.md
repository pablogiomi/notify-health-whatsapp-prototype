# WhatsApp Cloud API — a plain-language primer

This document explains how the WhatsApp Cloud API actually works, in plain language, for anyone evaluating whether to adopt WhatsApp as a messaging channel. No prior API experience assumed.

If you are reading this as part of reviewing the prototype, this is the same mental model the application is built on. Internalising this makes every code file more legible.

---

## 1. What an API is

API stands for *Application Programming Interface*. The name is fancier than the concept.

An API is a menu of actions a piece of software lets other software perform. The WhatsApp Cloud API's menu includes entries like "send a message," "upload a media file," and "list your approved templates." For each menu entry, the API specifies a URL, what information you have to include, and what you get back.

That is the whole idea. The rest is detail.

---

## 2. What a request looks like

A real (simplified) request to send a WhatsApp message:

```
POST /v23.0/123456789/messages HTTP/1.1
Host: graph.facebook.com
Authorization: Bearer EAAG...your_access_token...xyz
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "to": "+525512345678",
  "type": "template",
  "template": {
    "name": "hello_world",
    "language": { "code": "en_US" }
  }
}
```

Four things to notice.

**The URL.** `/v23.0/123456789/messages` means "create a new message belonging to phone number `123456789`." (Meta assigns you this ID when you set up a test business number.) This "verb + noun" structure — `POST /resource` to create, `GET /resource` to read — is called REST and is the dominant style for web APIs.

**The `Authorization` header.** An access token is a long random string that proves your identity to Meta. Think of it as a hotel keycard: anyone holding it gets in, so you guard it. **Never commit tokens to source control.** The prototype stores the token in an environment variable.

**The `Content-Type: application/json` header.** Tells Meta the body is in JSON format — key-value pairs, nested freely, readable by both humans and code. JSON is the lingua franca of web APIs.

**The body.** The actual instruction: "Send a template message, specifically `hello_world`, in `en_US`, to this number." Structured, not free text. Machines parse it reliably.

Meta's response:

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "messaging_product": "whatsapp",
  "contacts": [{"input": "+525512345678", "wa_id": "525512345678"}],
  "messages": [{"id": "wamid.HBgNMTUx..."}]
}
```

The important field is `messages[0].id` — the `wamid.X` string. This is Meta's identifier for the message you just sent. Your application stores it in the database and uses it later to link incoming status callbacks to this specific message.

---

## 3. Templates — the thing that surprises everyone

A WhatsApp business account **cannot send arbitrary text to a recipient who has not messaged it in the last 24 hours.** Meta enforces this to prevent spam.

Outgoing messages fall into two categories:

- **Freeform messages.** Regular text, images, audio. Allowed only during an open "customer service window" — the 24 hours following an inbound message from the recipient.
- **Template messages.** Pre-approved message structures with variable slots. Allowed at any time.

For a reminder service like Notify Health's use case, **templates are the only option.** The recipient has not messaged you; you are initiating the contact.

A template is submitted to Meta for approval once and then reused. A template looks like this when you submit it:

```
Category:  Utility
Name:      vaccination_reminder
Language:  English
Body:      "Hi {{1}}, this is a reminder that {{2}} is due for 
            their {{3}} vaccination on {{4}}. Reply with any questions."
```

`{{1}}`, `{{2}}`, and so on are parameter slots. When you actually send, you fill them:

```json
{
  "type": "template",
  "template": {
    "name": "vaccination_reminder",
    "language": {"code": "en"},
    "components": [{
      "type": "body",
      "parameters": [
        {"type": "text", "text": "Amina"},
        {"type": "text", "text": "Fatuma"},
        {"type": "text", "text": "measles"},
        {"type": "text", "text": "28 April"}
      ]
    }]
  }
}
```

Amina receives: *"Hi Amina, this is a reminder that Fatuma is due for their measles vaccination on 28 April. Reply with any questions."*

### Template approval

Meta reviews every new template before it can be used. Review typically takes a few hours to a few days. Templates can be rejected for wording that looks promotional, misleading, or otherwise non-compliant. Categories (Utility / Authentication / Marketing / Service) have different rules and different per-message prices.

For a production rollout with Notify Health, the workflow would be:

1. Draft reminder copy with your partners.
2. Submit to Meta for approval, one template per language.
3. Iterate on any rejections.
4. Once approved, use from your code.

The prototype sidesteps this entirely by using the pre-approved `hello_world` template that ships with every test account. The architecture handles template name as configuration, so swapping in a real template later is not a code change.

---

## 4. The two directions of traffic

One insight clarifies the entire system: the application and Meta talk to each other in **both directions**.

- **Application → Meta**: "please send this message." Immediate HTTP response (a receipt).
- **Meta → Application**: "by the way, that message you asked me to send was delivered." Arrives asynchronously, sometimes seconds, sometimes minutes later.

The second direction is called a **webhook**. It is the core reason the application must be more than a script — it has to be a web server that Meta can reach.

### Why asynchronous?

Imagine Meta tried to answer "was it delivered?" in the same HTTP response as "please send." Meta would have to wait for the recipient's phone to come online, for WhatsApp's network to route the message, for the delivery confirmation to come back — potentially seconds or minutes. Your request would hang. If the phone is off for an hour, your request would either time out or block your server for an hour.

The async pattern solves this: Meta accepts responsibility instantly ("OK, here's a receipt"), does the real work in the background, and reports back later on a separate connection. This pattern shows up everywhere — payments, shipping, food delivery, email — for the same reason.

---

## 5. Webhooks in detail

For Meta to call the application, the application must be reachable from the public internet. "My laptop at home" is not reachable. Options:

- **Development:** use a tunnelling tool like ngrok that gives a temporary public URL forwarded to the local machine.
- **Production:** deploy the application to a host with a public HTTPS URL (e.g. Railway).

### Registering the webhook

Once the application has a public URL, tell Meta about it in the developer dashboard. Registration involves a small security handshake:

```
Meta → your server: GET /webhook?hub.mode=subscribe
                                 &hub.verify_token=YOUR_SECRET
                                 &hub.challenge=RANDOM_STRING
Your server → Meta: responds with the RANDOM_STRING value
Meta: "OK, you control this endpoint. I'll send you events."
```

The `hub.verify_token` is a secret you make up and tell Meta at registration time. When Meta comes to verify, your server checks the token matches what it expects, and if so echoes the challenge. If a random person tries to point your webhook URL at their account, they can't echo the right challenge because they don't have the token.

### The webhook payload

When a message you sent gets delivered, Meta POSTs something like this to your webhook URL:

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "YOUR_WABA_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": { "display_phone_number": "...", "phone_number_id": "..." },
        "statuses": [{
          "id": "wamid.HBgNMTUx...",
          "status": "delivered",
          "timestamp": "1713704815",
          "recipient_id": "525512345678"
        }]
      },
      "field": "messages"
    }]
  }]
}
```

The important field is `statuses[0].id` — the same `wamid` Meta gave you when you sent the message. That `wamid` is the thread connecting the two halves: the original send response and the later webhook events. The application's webhook handler:

1. Verifies the `X-Hub-Signature-256` header (HMAC signed by Meta using the app secret).
2. Extracts the `wamid` and status from the payload.
3. Looks up the row in the `messages` table by `meta_message_id`.
4. Inserts a row in `message_events`.
5. Updates `messages.current_status`.
6. Responds `200 OK` to Meta.

If the application fails to respond `200`, Meta retries with exponential backoff. This is useful: brief server downtime does not mean lost events.

---

## 6. The five statuses

A message goes through some subset of these:

- **`sent`** — Meta accepted it and passed it on. Arrives a second or two after the original send.
- **`delivered`** — the recipient's device received it. They have internet, WhatsApp is installed, the message is in their inbox.
- **`read`** — the recipient opened the message. **Only fires if they have read receipts enabled in WhatsApp settings.** Many people disable this. Absence of `read` does not mean unread.
- **`failed`** — something went wrong. Comes with an `error_code` (e.g. `131026` = message undeliverable, `131051` = unsupported message type, `131047` = outside 24-hour window). Full list in Meta's docs.
- **`deleted`** — rare; the sender deleted the message.

Not every message hits every status. A message to a number not on WhatsApp might go `sent → failed`. A message to someone with read receipts off might go `sent → delivered` and stay there forever.

---

## 7. Common failure modes

Three things that cause most problems during development:

**Access token expired.** The dashboard-generated token lasts 24 hours. Requests with an expired token return HTTP `401 Unauthorized`. In production, use a long-lived "System User" token instead.

**Webhook URL changed.** Free ngrok tunnels get a new URL every restart. Meta needs to be told the new URL, or events go to the old (dead) address. Production deployments on Railway have a stable URL.

**Recipient not verified.** In test mode, only 5 verified numbers can receive messages. The recipient must confirm a code sent to their WhatsApp. Skipping this is the single most common "why isn't my message arriving" moment.

---

## 8. The summary

Three ideas are enough to understand the whole platform:

1. **Two flows, linked by `wamid`.** Send a request, get a `wamid`. Receive webhooks later with the same `wamid`. The application's database is what ties them together.
2. **Templates are mandatory for business-initiated messages.** Pre-approved structures with parameter slots. The application handles template name as a config value; the specific content is policy, not code.
3. **Webhooks need a public HTTPS URL.** Register it with Meta; handle the verification handshake; respond `200 OK` to every event.

Everything else — media messages, interactive buttons, WhatsApp Flows, inbound conversation handling — is a variation on these three ideas.
