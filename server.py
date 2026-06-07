"""
MCP-Style Server

FastAPI application exposing Google Docs and Gmail tools as POST endpoints.
- Local mode: human-in-the-loop terminal approval
- Production mode (Railway): API key authentication via MCP_API_KEY env var
"""

import os
import sys
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import uvicorn

from docs_tool import append_to_doc
from gmail_tool import create_email_draft


# ─── Configuration ────────────────────────────────────────────────────────────

# If MCP_API_KEY is set, run in production mode (no terminal approval, use API key)
API_KEY = os.environ.get("MCP_API_KEY")
PRODUCTION_MODE = API_KEY is not None


# ─── Request Models ───────────────────────────────────────────────────────────

class AppendDocRequest(BaseModel):
    doc_id: str
    content: str


class CreateDraftRequest(BaseModel):
    to: str
    subject: str
    body: str


# ─── Approval / Auth Helper ───────────────────────────────────────────────────

def verify_api_key(x_api_key: str = Header(None)):
    """Dependency that checks API key in production mode."""
    if PRODUCTION_MODE:
        if not x_api_key or x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return True


def request_approval(action: str, payload: dict) -> bool:
    """
    In local mode: print action and payload to terminal and ask for approval.
    In production mode: skip (already authenticated via API key).
    """
    if PRODUCTION_MODE:
        print(f"✅ [PRODUCTION] Auto-approved: {action} | {payload}")
        return True

    print("\n" + "=" * 60)
    print(f"🔔 ACTION REQUESTED: {action}")
    print("-" * 60)
    for key, value in payload.items():
        print(f"  {key}: {value}")
    print("=" * 60)

    try:
        response = input("Approve? (y/n): ").strip().lower()
        return response == "y"
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Approval denied (interrupted).")
        return False


# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Google MCP Server",
    description="MCP-style server for Google Docs and Gmail integration",
    version="1.0.0",
)


@app.get("/")
def root():
    """Health check / info endpoint."""
    return {
        "server": "Google MCP Server",
        "version": "1.0.0",
        "tools": [
            {"name": "append_to_doc", "endpoint": "POST /append_to_doc"},
            {"name": "create_email_draft", "endpoint": "POST /create_email_draft"},
        ],
    }


@app.post("/append_to_doc")
def handle_append_to_doc(request: AppendDocRequest, _auth=Depends(verify_api_key)):
    """
    Append text content to a Google Doc.
    Requires terminal approval (local) or API key (production).
    """
    payload = {"doc_id": request.doc_id, "content": request.content}

    if not request_approval("Append to Google Doc", payload):
        raise HTTPException(status_code=403, detail="Action denied by user.")

    try:
        result = append_to_doc(doc_id=request.doc_id, content=request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create_email_draft")
def handle_create_email_draft(request: CreateDraftRequest, _auth=Depends(verify_api_key)):
    """
    Create a draft email in Gmail.
    Requires terminal approval (local) or API key (production).
    """
    payload = {"to": request.to, "subject": request.subject, "body": request.body}

    if not request_approval("Create Gmail Draft", payload):
        raise HTTPException(status_code=403, detail="Action denied by user.")

    try:
        result = create_email_draft(to=request.to, subject=request.subject, body=request.body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mode = "PRODUCTION" if PRODUCTION_MODE else "LOCAL"
    print(f"🚀 Starting Google MCP Server on http://0.0.0.0:{port} [{mode} mode]")
    print("   Endpoints:")
    print("     POST /append_to_doc")
    print("     POST /create_email_draft")
    print("   Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
