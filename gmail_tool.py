"""
Gmail Tool

Provides functionality to create email drafts in Gmail.
"""

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from auth import get_credentials


def create_email_draft(to: str, subject: str, body: str) -> dict:
    """
    Create a draft email in the authenticated user's Gmail.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain text email body.

    Returns:
        A dict with the status and draft details.
    """
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    # Build the MIME message
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    # Encode to base64url
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    # Create the draft
    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw_message}},
    ).execute()

    return {
        "status": "success",
        "draft_id": draft["id"],
        "message": f"Draft created successfully. To: {to}, Subject: {subject}",
    }
