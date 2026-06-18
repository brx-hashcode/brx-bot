# GitHub Bot — Claude-powered assistant

Automatically responds to GitHub events on your behalf using Claude, and notifies you on Slack.

## Events handled

| Event | Trigger | Claude action |
|---|---|---|
| Issue opened | New issue in your repos | Acknowledges + asks clarifying questions |
| Issue assigned | Issue assigned to you | Confirms assignment + next steps |
| PR assigned | PR assigned to you | Reviews diff + acknowledges |
| @mention | Anyone mentions you in a comment | Replies directly to the question |

---

## Setup

### 1. Create a GitHub App (or use a Personal Access Token)

**Option A — Personal Access Token (easiest for local)**
1. Go to https://github.com/settings/tokens → Generate new token (classic)
2. Scopes: `repo`, `write:discussion`
3. Copy the token → `GITHUB_TOKEN` in `.env`

**Option B — GitHub App (more secure)**
1. Go to https://github.com/settings/apps → New GitHub App
2. Webhook URL: `https://<your-tunnel>/github/webhook`
3. Webhook secret: any random string → `WEBHOOK_SECRET` in `.env`
4. Subscribe to: Issues, Pull requests, Issue comments
5. Permissions: Issues (Read & Write), Pull requests (Read & Write)
6. Install the app on your repos

### 2. Create a Slack Incoming Webhook
1. Go to https://api.slack.com/apps → Create New App → From scratch
2. Features → Incoming Webhooks → Activate
3. Add New Webhook to Workspace → pick your channel
4. Copy the webhook URL → `SLACK_WEBHOOK_URL` in `.env`

### 3. Configure environment

```bash
cp .env.example .env
# Fill in all values
```

### 4. Install dependencies & run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

### 5. Expose locally with ngrok or cloudflared

```bash
# ngrok
ngrok http 8000

# OR cloudflared (if you already have it set up)
cloudflared tunnel --url http://localhost:8000
```

Set the tunnel URL as your GitHub App webhook URL:
`https://<tunnel-id>.trycloudflare.com/github/webhook`

---

## Project structure

```
github-bot/
├── app/
│   ├── main.py              # FastAPI app + webhook router
│   ├── config.py            # Env vars
│   ├── handlers/
│   │   ├── issue.py         # issue_opened, issue_assigned
│   │   ├── pr.py            # pr_assigned
│   │   └── comment.py       # @mention handler
│   └── services/
│       ├── claude.py        # Anthropic API wrapper
│       ├── github.py        # GitHub API calls
│       └── slack.py         # Slack Incoming Webhook
├── requirements.txt
├── .env.example
└── README.md
```

---

## Loop prevention

The bot skips comments made by your own username or the bot name to avoid infinite reply loops. Comment IDs are tracked in memory (restart clears them). For production, swap with a Redis set.

---

## Deploying to VPS later

When you're ready to move from local to your Contabo VPS:
1. Add a `Dockerfile` + `docker-compose.yml`
2. Add a Traefik label for routing
3. Point your GitHub App webhook URL to `https://github-bot.yourdomain.com/github/webhook`
# brx-bot
