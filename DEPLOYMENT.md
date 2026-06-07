# 🚀 Railway Deployment Plan — Google MCP Server

## Overview

Deploy the Google MCP Server as a publicly accessible FastAPI service on [Railway](https://railway.app). Since Railway doesn't have a terminal for interactive approval, we use **API key authentication** in production instead.

---

## Architecture (Production)

```
Client (AI Agent / curl)
    │
    │  POST /append_to_doc or /create_email_draft
    │  Header: X-API-Key: <your-secret>
    ▼
┌─────────────────────────┐
│   Railway (FastAPI)     │
│   - Validates API key   │
│   - Calls Google APIs   │
│   - Returns result      │
└─────────────────────────┘
    │
    ▼
Google Docs API / Gmail API
```

---

## Pre-Deployment Checklist

| # | Task | Status |
|---|------|--------|
| 1 | Generate `token.json` locally (already done ✅) | ✅ |
| 2 | Push code to GitHub (without secrets) | ⬜ |
| 3 | Create Railway project | ⬜ |
| 4 | Set environment variables on Railway | ⬜ |
| 5 | Deploy and verify health check | ⬜ |
| 6 | Test endpoints with curl | ⬜ |

---

## Step-by-Step Deployment

### Step 1: Prepare the Token for Railway

Railway can't open a browser for OAuth. You'll pass the token as an environment variable.

```bash
# From the project directory, copy your token.json contents:
cat token.json | pbcopy
```

This is the value you'll paste into Railway's `GOOGLE_TOKEN_JSON` env var.

---

### Step 2: Push to GitHub

```bash
cd google-mcp-server
git init
git add .
git commit -m "Initial commit: Google MCP Server"
git remote add origin https://github.com/YOUR_USERNAME/google-mcp-server.git
git push -u origin main
```

> ⚠️ `credentials.json` and `token.json` are in `.gitignore` — they won't be committed.

---

### Step 3: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Select your `google-mcp-server` repository
4. Railway will auto-detect Python and use `requirements.txt`

---

### Step 4: Set Environment Variables

In the Railway dashboard, go to your service → **Variables** tab and add:

| Variable | Value | Description |
|----------|-------|-------------|
| `GOOGLE_TOKEN_JSON` | *(paste entire contents of token.json)* | OAuth token for Google APIs |
| `MCP_API_KEY` | *(generate a strong random string)* | Protects your endpoints |
| `PORT` | `8000` | *(Railway sets this automatically, but you can be explicit)* |

**Generate a secure API key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### Step 5: Deploy

Railway will auto-deploy on push. It will:
1. Detect Python via `requirements.txt`
2. Install dependencies
3. Run: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Hit the `/` health check endpoint

You'll see a public URL like: `https://google-mcp-server-production-xxxx.up.railway.app`

---

### Step 6: Verify Deployment

```bash
# Health check
curl https://YOUR-RAILWAY-URL.up.railway.app/

# Test append to doc
curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/append_to_doc \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_MCP_API_KEY" \
  -d '{"doc_id": "YOUR_DOC_ID", "content": "Hello from Railway!"}'

# Test create draft
curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/create_email_draft \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_MCP_API_KEY" \
  -d '{"to": "test@example.com", "subject": "Test", "body": "Deployed on Railway!"}'
```

---

## Files Added/Modified for Railway

| File | Purpose |
|------|---------|
| `Procfile` | Tells Railway how to start the app |
| `railway.toml` | Railway-specific config (health check, restart policy) |
| `.python-version` | Pins Python 3.11 for Railway's Nixpacks builder |
| `auth.py` | Updated to load token from `GOOGLE_TOKEN_JSON` env var |
| `server.py` | Added API key auth, uses `PORT` env var, production mode |

---

## Environment Modes

| Mode | Trigger | Auth | Approval |
|------|---------|------|----------|
| **Local** | No `MCP_API_KEY` set | None (terminal) | Interactive `y/n` prompt |
| **Production** | `MCP_API_KEY` is set | `X-API-Key` header | Auto-approved (logged) |

---

## Token Refresh Strategy

The Google OAuth token expires every ~1 hour, but includes a **refresh token** that lasts indefinitely (unless revoked). The server auto-refreshes expired tokens using the refresh token embedded in `GOOGLE_TOKEN_JSON`.

**If the token stops working:**
1. Run locally: `venv/bin/python -c "from auth import get_credentials; get_credentials()"`
2. Copy the new `token.json` contents
3. Update the `GOOGLE_TOKEN_JSON` variable on Railway
4. Railway will auto-redeploy

---

## Security Notes

- Never commit `credentials.json` or `token.json` to git
- Rotate `MCP_API_KEY` periodically
- Use Railway's private networking if calling from another Railway service
- Consider adding rate limiting for public deployments (e.g., `slowapi`)

---

## Cost

Railway free tier includes:
- $5/month credit (enough for light usage)
- 512 MB RAM, shared CPU
- Auto-sleep after 15 min inactivity (wakes on request)

For always-on: upgrade to Hobby plan ($5/month).
