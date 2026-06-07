"""
Google Docs Tool

Provides functionality to append content to a Google Doc.
"""

from googleapiclient.discovery import build
from auth import get_credentials


def append_to_doc(doc_id: str, content: str) -> dict:
    """
    Append text content to the end of a Google Doc.

    Args:
        doc_id: The ID of the Google Doc (from the URL).
        content: The text content to append.

    Returns:
        A dict with the status and document ID.
    """
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    # Get the document to find the end index
    document = service.documents().get(documentId=doc_id).execute()
    end_index = document["body"]["content"][-1]["endIndex"] - 1

    # Build the append request
    requests = [
        {
            "insertText": {
                "location": {"index": end_index},
                "text": content + "\n",
            }
        }
    ]

    # Execute the batch update
    result = service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    return {
        "status": "success",
        "document_id": doc_id,
        "message": f"Appended {len(content)} characters to document.",
        "replies": result.get("replies", []),
    }
