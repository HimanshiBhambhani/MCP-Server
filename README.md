# Google MCP Server

An MCP-style (Model Context Protocol) server built with FastAPI that integrates with **Google Docs** and **Gmail**. It exposes tool endpoints that an AI agent can call, with human-in-the-loop approval before any action is executed.

## Features

- **Append to Google Doc** — Append text content to any Google Doc you have access to
- **Create Gmail Draft** — Create a draft email in your Gmail account
- **Human-in-the-loop** — Every action requires terminal approval before execution

---

## Project Structure

```
google-mcp-server/
├── server.py          → FastAPI app with tool endpoints
├── auth.py            → Google OAuth authentication
├── docs_tool.py       → Google Docs tool (append content)
├── gmail_tool.py      → Gmail tool (create draft)
├── requirements.txt   → All dependencies
├── README.md          → This file
├── credentials.json   → (NOT committed — from Google Cloud Console)
└── token.json         → (NOT committed — auto-generated after OAuth)
```

---

## Prerequisites

- Python 3.10+
- A Google Cloud project with:
  - **Google Docs API** enabled
  - **Gmail API** enabled
  - **OAuth 2.0 credentials** (Desktop application type)

---

## Setup

### 1. Google Cloud Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the following APIs:
   - Google Docs API
   - Gmail API
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Select **Desktop app** as the application type
6. Download the JSON file and save it as `credentials.json` in the project root

### 2. Install Dependencies

```bash
cd google-mcp-server
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python server.py
```

On first run, a browser window will open asking you to authorize the application. After authorization, a `token.json` file is created — subsequent runs won't require browser auth.

The server starts at `http://localhost:8000`.

---

## API Endpoints

### `GET /`

Health check. Returns server info and available tools.

### `POST /append_to_doc`

Append text to a Google Doc.

**Request body:**
```json
{
  "doc_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
  "content": "Hello from MCP server!"
}
```

**Response:**
```json
{
  "status": "success",
  "document_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
  "message": "Appended 22 characters to document.",
  "replies": []
}
```

### `POST /create_email_draft`

Create a draft email in Gmail.

**Request body:**
```json
{
  "to": "recipient@example.com",
  "subject": "Meeting Notes",
  "body": "Hi, here are the notes from today's meeting..."
}
```

**Response:**
```json
{
  "status": "success",
  "draft_id": "r123456789",
  "message": "Draft created successfully. To: recipient@example.com, Subject: Meeting Notes"
}
```

---

## Human-in-the-Loop Approval

Every action prints details to the terminal and asks for confirmation:

```
============================================================
🔔 ACTION REQUESTED: Append to Google Doc
------------------------------------------------------------
  doc_id: 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
  content: Hello from MCP server!
============================================================
Approve? (y/n): 
```

Type `y` to proceed or `n` to deny the action (returns HTTP 403).

---

## Usage with curl

```bash
# Append to a Google Doc
curl -X POST http://localhost:8000/append_to_doc \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "YOUR_DOC_ID", "content": "Hello World"}'

# Create a Gmail draft
curl -X POST http://localhost:8000/create_email_draft \
  -H "Content-Type: application/json" \
  -d '{"to": "someone@example.com", "subject": "Test", "body": "This is a test draft."}'
```

---

## .gitignore Recommendation

Add these to your `.gitignore`:

```
credentials.json
token.json
__pycache__/
*.pyc
.env
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `credentials.json not found` | Download OAuth credentials from Google Cloud Console |
| Token expired errors | Delete `token.json` and re-run to re-authenticate |
| API not enabled | Enable Google Docs API and Gmail API in Cloud Console |
| Permission denied on doc | Ensure your Google account has edit access to the doc |

---

## License

MIT
