import json
import logging

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

# ruff: noqa: E501
SYSTEM_PROMPT = (
    "You are a financial transaction detector. "
    "You analyze emails and determine if they contain financial movements "
    "(charges, payments, transfers, deposits, purchases, subscriptions, etc.).\n\n"
    "IMPORTANT RULES:\n"
    "- Only detect ACTUAL financial transactions, not marketing emails about deals or promotions.\n"
    "- Extract data EXACTLY as it appears in the email. Do not invent or guess amounts.\n"
    "- Dates should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).\n"
    "- Currency should be a 3-letter ISO code (MXN, USD, EUR, etc.). Default to MXN if unclear.\n"
    "- Type must be one of: 'income', 'expense', 'transfer'.\n"
    "- If you cannot determine a field with confidence, use null.\n"
    "- A single email may contain multiple transactions (e.g., a bank statement summary).\n"
    "- Respond ONLY with valid JSON, no markdown, no explanation."
)

EXTRACTION_PROMPT = """Analyze this email and extract any financial transactions.

**Email subject:** {subject}
**From:** {sender}
**Date:** {date}
**Body:**
{body}

Respond with a JSON object in this exact format:
{{
  "has_movement": true/false,
  "movements": [
    {{
      "type": "expense" | "income" | "transfer",
      "amount": 123.45,
      "currency": "MXN",
      "account": "card or account name if mentioned, else null",
      "movement_date": "2026-03-29T10:30:00",
      "concept": "brief description of what the charge is for",
      "merchant": "business/merchant name if identifiable, else null",
      "suggested_category": "suggested category name based on the type of expense"
    }}
  ]
}}

If the email does NOT contain a financial transaction, respond:
{{
  "has_movement": false,
  "movements": []
}}"""


def _get_client() -> anthropic.Anthropic:
    """Create an Anthropic client."""
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not configured. Set it in your .env file."
        )
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def analyze_email(email: dict, max_retries: int = 2) -> dict:
    """
    Analyze a single email using Claude to detect financial movements.

    Args:
        email: Dict with keys: subject, sender, date, body, snippet.
        max_retries: Number of retries on failure.

    Returns:
        Dict with has_movement (bool) and movements (list).
    """
    client = _get_client()

    prompt = EXTRACTION_PROMPT.format(
        subject=email.get("subject", ""),
        sender=email.get("sender", ""),
        date=email.get("date", ""),
        body=email.get("body", email.get("snippet", "")),
    )

    for attempt in range(max_retries + 1):
        try:
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text.strip()

            # Parse JSON response
            result = json.loads(response_text)

            # Validate structure
            if "has_movement" not in result:
                result["has_movement"] = bool(result.get("movements"))
            if "movements" not in result:
                result["movements"] = []

            return result

        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse AI response as JSON (attempt %d): %s",
                attempt + 1,
                response_text[:200] if "response_text" in dir() else "no response",
            )
            if attempt == max_retries:
                return {
                    "has_movement": False,
                    "movements": [],
                    "error": "parse_error",
                }

        except anthropic.APIError as e:
            logger.error(
                "Anthropic API error (attempt %d): %s",
                attempt + 1,
                str(e),
            )
            if attempt == max_retries:
                return {
                    "has_movement": False,
                    "movements": [],
                    "error": str(e),
                }

    return {"has_movement": False, "movements": []}


def analyze_emails(emails: list[dict]) -> list[dict]:
    """
    Analyze a batch of emails for financial movements.

    Args:
        emails: List of email dicts from Gmail service.

    Returns:
        List of dicts, each containing:
        - email_id: Gmail message ID
        - subject: Email subject
        - analysis: The AI analysis result
    """
    results = []

    for email in emails:
        analysis = analyze_email(email)
        results.append(
            {
                "email_id": email["id"],
                "subject": email.get("subject", ""),
                "sender": email.get("sender", ""),
                "date": email.get("date", ""),
                "analysis": analysis,
            }
        )

    return results
