"""
Google OAuth 2.0 Authentication Module (Production-Ready)

Supports two modes:
  - LOCAL: Uses credentials.json + token.json with browser-based OAuth
  - PRODUCTION (Railway): Loads token from GOOGLE_TOKEN_JSON environment variable
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for Google Docs and Gmail
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.compose",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_credentials() -> Credentials:
    """
    Load or generate Google OAuth credentials.

    Production (Railway):
      - Reads token JSON from GOOGLE_TOKEN_JSON env var
      - Automatically refreshes if expired

    Local:
      - If token.json exists and is valid, load it directly.
      - If the token is expired but has a refresh token, refresh it.
      - Otherwise, run the OAuth browser flow using credentials.json.
    """
    creds = None

    # --- Production mode: load from environment variable ---
    token_json_env = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_json_env:
        token_data = json.loads(token_json_env)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise RuntimeError(
                    "Token from GOOGLE_TOKEN_JSON is invalid and cannot be refreshed. "
                    "Re-generate token.json locally and update the env var."
                )
        return creds

    # --- Local mode: file-based token ---
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_FILE}' not found. Download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the token for future runs
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return creds
