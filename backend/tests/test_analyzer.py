import json
from unittest.mock import MagicMock, patch

from app.services.analyzer import analyze_email, analyze_emails


def _mock_claude_response(content: dict) -> MagicMock:
    """Create a mock Claude API response."""
    mock_message = MagicMock()
    mock_content = MagicMock()
    mock_content.text = json.dumps(content)
    mock_message.content = [mock_content]
    return mock_message


@patch("app.services.analyzer._get_client")
def test_analyze_email_detects_expense(mock_get_client):
    """Detects a financial movement in an email."""
    ai_response = {
        "has_movement": True,
        "movements": [
            {
                "type": "expense",
                "amount": 450.00,
                "currency": "MXN",
                "account": "BBVA Débito",
                "movement_date": "2026-03-29T14:30:00",
                "concept": "Compra en supermercado",
                "merchant": "Walmart",
                "suggested_category": "Supermercado",
            }
        ],
    }

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_claude_response(ai_response)
    mock_get_client.return_value = mock_client

    email = {
        "id": "msg1",
        "subject": "Compra realizada - BBVA",
        "sender": "avisos@bbva.mx",
        "date": "2026-03-29T14:30:00",
        "body": (
            "Se realizó una compra por $450.00 MXN "
            "en Walmart con tu tarjeta BBVA Débito."
        ),
    }

    result = analyze_email(email)
    assert result["has_movement"] is True
    assert len(result["movements"]) == 1
    assert result["movements"][0]["amount"] == 450.00
    assert result["movements"][0]["merchant"] == "Walmart"


@patch("app.services.analyzer._get_client")
def test_analyze_email_no_movement(mock_get_client):
    """Correctly identifies non-financial emails."""
    ai_response = {"has_movement": False, "movements": []}

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_claude_response(ai_response)
    mock_get_client.return_value = mock_client

    email = {
        "id": "msg2",
        "subject": "Newsletter semanal",
        "sender": "news@example.com",
        "date": "2026-03-29T10:00:00",
        "body": "Aquí están las noticias de la semana...",
    }

    result = analyze_email(email)
    assert result["has_movement"] is False
    assert len(result["movements"]) == 0


@patch("app.services.analyzer._get_client")
def test_analyze_email_handles_invalid_json(mock_get_client):
    """Returns safe default when AI returns invalid JSON."""
    mock_message = MagicMock()
    mock_content = MagicMock()
    mock_content.text = "This is not JSON"
    mock_message.content = [mock_content]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    mock_get_client.return_value = mock_client

    email = {
        "id": "msg3",
        "subject": "Test",
        "sender": "test@test.com",
        "date": "2026-03-29T10:00:00",
        "body": "Test body",
    }

    result = analyze_email(email, max_retries=0)
    assert result["has_movement"] is False
    assert "error" in result


@patch("app.services.analyzer._get_client")
def test_analyze_email_multiple_movements(mock_get_client):
    """Detects multiple movements in a single email."""
    ai_response = {
        "has_movement": True,
        "movements": [
            {
                "type": "expense",
                "amount": 199.00,
                "currency": "MXN",
                "account": "Amex",
                "movement_date": "2026-03-29T10:00:00",
                "concept": "Netflix",
                "merchant": "Netflix",
                "suggested_category": "Entretenimiento",
            },
            {
                "type": "expense",
                "amount": 115.00,
                "currency": "MXN",
                "account": "Amex",
                "movement_date": "2026-03-29T10:00:00",
                "concept": "Spotify",
                "merchant": "Spotify",
                "suggested_category": "Entretenimiento",
            },
        ],
    }

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_claude_response(ai_response)
    mock_get_client.return_value = mock_client

    email = {
        "id": "msg4",
        "subject": "Estado de cuenta",
        "sender": "amex@americanexpress.com",
        "date": "2026-03-29T10:00:00",
        "body": "Tus cargos: Netflix $199, Spotify $115",
    }

    result = analyze_email(email)
    assert result["has_movement"] is True
    assert len(result["movements"]) == 2


@patch("app.services.analyzer.analyze_email")
def test_analyze_emails_batch(mock_analyze):
    """Processes a batch of emails."""
    mock_analyze.side_effect = [
        {"has_movement": True, "movements": [{"amount": 100}]},
        {"has_movement": False, "movements": []},
    ]

    emails = [
        {
            "id": "msg1",
            "subject": "Compra",
            "sender": "bank@test.com",
            "date": "2026-03-29",
        },
        {
            "id": "msg2",
            "subject": "Newsletter",
            "sender": "news@test.com",
            "date": "2026-03-29",
        },
    ]

    results = analyze_emails(emails)
    assert len(results) == 2
    assert results[0]["analysis"]["has_movement"] is True
    assert results[1]["analysis"]["has_movement"] is False
