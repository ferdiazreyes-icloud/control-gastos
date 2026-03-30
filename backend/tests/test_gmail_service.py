import base64
from unittest.mock import MagicMock, patch

from app.services.gmail import _decode_body, _extract_header, fetch_emails


def test_extract_header():
    """Extracts a header value by name."""
    headers = [
        {"name": "Subject", "value": "Test Subject"},
        {"name": "From", "value": "test@example.com"},
        {"name": "Date", "value": "Mon, 29 Mar 2026 10:00:00 -0600"},
    ]
    assert _extract_header(headers, "Subject") == "Test Subject"
    assert _extract_header(headers, "From") == "test@example.com"
    assert _extract_header(headers, "Missing") == ""


def test_decode_body_plain_text():
    """Decodes a plain text email body."""
    text = "Hello, this is a test email."
    encoded = base64.urlsafe_b64encode(text.encode()).decode()
    payload = {"body": {"data": encoded}}
    assert _decode_body(payload) == text


def test_decode_body_multipart():
    """Decodes body from multipart email."""
    text = "Multipart body text"
    encoded = base64.urlsafe_b64encode(text.encode()).decode()
    payload = {
        "body": {},
        "parts": [
            {"mimeType": "text/plain", "body": {"data": encoded}},
            {"mimeType": "text/html", "body": {"data": encoded}},
        ],
    }
    assert _decode_body(payload) == text


def test_decode_body_empty():
    """Returns empty string when no body found."""
    payload = {"body": {}, "parts": []}
    assert _decode_body(payload) == ""


@patch("app.services.gmail._get_gmail_service")
def test_fetch_emails_empty(mock_service):
    """Returns empty list when no messages found."""
    mock_gmail = MagicMock()
    mock_gmail.users().messages().list().execute.return_value = {"messages": []}
    mock_service.return_value = mock_gmail

    result = fetch_emails(max_results=10)
    assert result == []


@patch("app.services.gmail._get_gmail_service")
def test_fetch_emails_skips_processed(mock_service):
    """Skips already processed email IDs."""
    mock_gmail = MagicMock()
    mock_gmail.users().messages().list().execute.return_value = {
        "messages": [
            {"id": "msg1"},
            {"id": "msg2"},
            {"id": "msg3"},
        ]
    }

    text = "Test email body"
    encoded = base64.urlsafe_b64encode(text.encode()).decode()
    mock_gmail.users().messages().get().execute.return_value = {
        "id": "msg2",
        "snippet": "Test",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test"},
                {"name": "From", "value": "test@test.com"},
                {"name": "Date", "value": "Mon, 29 Mar 2026 10:00:00 -0600"},
            ],
            "body": {"data": encoded},
        },
    }
    mock_service.return_value = mock_gmail

    result = fetch_emails(max_results=10, processed_ids={"msg1", "msg3"})
    assert len(result) == 1
    assert result[0]["id"] == "msg2"
