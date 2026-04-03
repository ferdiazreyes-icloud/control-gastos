import base64
import json
import os
import re
from email.utils import parsedate_to_datetime
from typing import Optional

from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.config import settings

# Path to store OAuth tokens (single user, file-based for MVP)
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")
STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "oauth_state.json")

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


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


def _create_flow() -> Flow:
    """Create a new OAuth flow instance."""
    return Flow.from_client_config(
        _get_client_config(),
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )


def get_auth_url() -> str:
    """Generate the Google OAuth authorization URL with PKCE."""
    # Remove old token to force fresh auth with new scopes
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)

    flow = _create_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    # Save flow state including code_verifier for PKCE
    state_data = {
        "state": state,
        "code_verifier": flow.code_verifier,
    }
    with open(STATE_PATH, "w") as f:
        json.dump(state_data, f)

    return auth_url


def exchange_code_for_tokens(code: str) -> dict:
    """Exchange the authorization code for access and refresh tokens."""
    flow = _create_flow()

    # Restore code_verifier from saved state for PKCE
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            state_data = json.load(f)
        flow.code_verifier = state_data.get("code_verifier")

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


def _strip_html(html: str) -> str:
    """Convert HTML to clean plain text for AI processing."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for element in soup(["script", "style", "head"]):
        element.decompose()

    # Get text and clean up whitespace
    text = soup.get_text(separator="\n")
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)

    return text


def _decode_body(payload: dict) -> str:
    """Extract and decode the email body text from a Gmail message payload."""
    # Check for direct body data
    if payload.get("body", {}).get("data"):
        raw = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        return _strip_html(raw) if "<" in raw else raw

    # Check multipart parts — prefer text/plain
    parts = payload.get("parts", [])
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

    # Fallback: text/html → strip to plain text
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/html" and part.get("body", {}).get("data"):
            html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
            return _strip_html(html)

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
    processed_ids: Optional[set] = None,
    sender_patterns: Optional[list[str]] = None,
) -> list[dict]:
    """
    Fetch all unprocessed emails from Gmail inbox, with pagination.

    Paginates through ALL inbox emails matching sender whitelist.
    Already-processed emails are skipped before fetching full details.
    After processing, emails should be archived via archive_emails().

    Args:
        processed_ids: Set of Gmail message IDs already processed (to skip).
        sender_patterns: List of sender email patterns to filter by
            (e.g. ["@santander.com.mx", "noreply@uber.com"]).

    Returns:
        Tuple of (new_emails, stale_inbox_ids):
        - new_emails: List of dicts with email data for unprocessed emails.
        - stale_inbox_ids: List of Gmail IDs for already-processed emails
          still in inbox (should be archived).
    """
    service = _get_gmail_service()

    # Build query: only inbox emails from whitelisted senders
    query_parts = ["in:inbox"]

    if sender_patterns:
        from_clauses = " OR ".join(f"from:{pattern}" for pattern in sender_patterns)
        query_parts.append(f"({from_clauses})")

    query = " ".join(query_parts)

    # List ALL matching messages with pagination
    all_message_refs = []
    next_page_token = None

    while True:
        params = {"userId": "me", "q": query, "maxResults": 500}
        if next_page_token:
            params["pageToken"] = next_page_token

        results = service.users().messages().list(**params).execute()
        messages = results.get("messages", [])
        all_message_refs.extend(messages)

        next_page_token = results.get("nextPageToken")
        if not next_page_token:
            break

    if not all_message_refs:
        return [], []

    # Separate already-processed emails (still in inbox) from new ones
    already_in_inbox = []
    new_message_refs = []
    for m in all_message_refs:
        if processed_ids and m["id"] in processed_ids:
            already_in_inbox.append(m["id"])
        else:
            new_message_refs.append(m)

    # Fetch full message details for new emails only
    emails = []
    for msg_ref in new_message_refs:
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

    return emails, already_in_inbox


def archive_emails(email_ids: list[str]) -> int:
    """
    Archive emails by removing the INBOX label.

    Args:
        email_ids: List of Gmail message IDs to archive.

    Returns:
        Number of emails successfully archived.
    """
    if not email_ids:
        return 0

    service = _get_gmail_service()
    archived = 0

    for email_id in email_ids:
        try:
            service.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["INBOX"]},
            ).execute()
            archived += 1
        except Exception:
            # Log but don't fail the whole pipeline for archive errors
            pass

    return archived
