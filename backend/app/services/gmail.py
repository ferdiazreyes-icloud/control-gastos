import base64
import json
import os
from email.utils import parsedate_to_datetime
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.config import settings

# Path to store OAuth tokens (single user, file-based for MVP)
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _get_client_config() -> dict:
    """Build the OAuth client config from environment variables."""
    return {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }


def get_auth_url() -> str:
    """Generate the Google OAuth authorization URL."""
    flow = Flow.from_client_config(
        _get_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url


def exchange_code_for_tokens(code: str) -> dict:
    """Exchange the authorization code for access and refresh tokens."""
    flow = Flow.from_client_config(
        _get_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials

    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    # Save tokens to file (single user, MVP approach)
    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f)

    return token_data


def get_credentials() -> Optional[Credentials]:
    """Load stored credentials, refreshing if needed."""
    if not os.path.exists(TOKEN_PATH):
        return None

    with open(TOKEN_PATH) as f:
        token_data = json.load(f)

    credentials = Credentials(
        token=token_data["token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data.get("scopes"),
    )

    return credentials


def is_authenticated() -> bool:
    """Check if we have valid stored credentials."""
    creds = get_credentials()
    return creds is not None


def _get_gmail_service():
    """Build the Gmail API service client."""
    credentials = get_credentials()
    if not credentials:
        raise RuntimeError("Not authenticated with Gmail. Please authenticate first.")
    return build("gmail", "v1", credentials=credentials)


def _decode_body(payload: dict) -> str:
    """Extract and decode the email body text from a Gmail message payload."""
    # Check for direct body data
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    # Check multipart parts
    parts = payload.get("parts", [])
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

    # Fallback: try text/html
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/html" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

    # Nested multipart
    for part in parts:
        if part.get("parts"):
            result = _decode_body(part)
            if result:
                return result

    return ""


def _extract_header(headers: list, name: str) -> str:
    """Extract a specific header value from Gmail message headers."""
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return ""


def fetch_emails(
    max_results: int = 50,
    after_date: Optional[str] = None,
    processed_ids: Optional[set] = None,
) -> list[dict]:
    """
    Fetch emails from Gmail.

    Args:
        max_results: Maximum number of emails to fetch.
        after_date: Only fetch emails after this date (format: YYYY/MM/DD).
        processed_ids: Set of Gmail message IDs already processed (to skip).

    Returns:
        List of dicts with email data: id, subject, sender, date, body.
    """
    service = _get_gmail_service()

    # Build query
    query_parts = []
    if after_date:
        query_parts.append(f"after:{after_date}")

    query = " ".join(query_parts) if query_parts else None

    # List messages
    results = (
        service.users()
        .messages()
        .list(userId="me", maxResults=max_results, q=query)
        .execute()
    )

    messages = results.get("messages", [])
    if not messages:
        return []

    # Filter out already processed emails
    if processed_ids:
        messages = [m for m in messages if m["id"] not in processed_ids]

    # Fetch full message details
    emails = []
    for msg_ref in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_ref["id"], format="full")
            .execute()
        )

        headers = msg.get("payload", {}).get("headers", [])
        subject = _extract_header(headers, "Subject")
        sender = _extract_header(headers, "From")
        date_str = _extract_header(headers, "Date")
        body = _decode_body(msg.get("payload", {}))

        # Parse date
        email_date = None
        if date_str:
            try:
                email_date = parsedate_to_datetime(date_str).isoformat()
            except (ValueError, TypeError):
                email_date = date_str

        emails.append(
            {
                "id": msg["id"],
                "subject": subject,
                "sender": sender,
                "date": email_date,
                "body": body[:5000],  # Limit body size for AI processing
                "snippet": msg.get("snippet", ""),
            }
        )

    return emails
