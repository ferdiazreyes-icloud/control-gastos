import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement, MovementStatus, MovementType
from app.models.processed_email import ProcessedEmail
from app.services.analyzer import analyze_emails
from app.services.gmail import fetch_emails

logger = logging.getLogger(__name__)


def _parse_movement_type(type_str: str) -> MovementType:
    """Convert string to MovementType enum."""
    type_map = {
        "income": MovementType.INCOME,
        "expense": MovementType.EXPENSE,
        "transfer": MovementType.TRANSFER,
    }
    return type_map.get(type_str.lower(), MovementType.EXPENSE)


def _parse_amount(amount) -> Optional[Decimal]:
    """Safely parse amount to Decimal."""
    if amount is None:
        return None
    try:
        return Decimal(str(amount)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a date string to datetime."""
    if not date_str:
        return None

    # Try ISO format first
    for fmt in [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


async def process_emails(
    db: AsyncSession,
    max_results: int = 50,
    after_date: Optional[str] = None,
) -> dict:
    """
    Full pipeline: fetch emails → analyze with AI → store movements.

    Args:
        db: Database session.
        max_results: Max emails to fetch from Gmail.
        after_date: Only fetch emails after this date (YYYY/MM/DD).

    Returns:
        Summary dict with counts of processed, detected, and stored movements.
    """
    # Step 1: Get already processed email IDs
    result = await db.execute(select(ProcessedEmail.gmail_message_id))
    processed_ids = {row[0] for row in result.all()}

    # Step 2: Fetch new emails from Gmail
    emails = fetch_emails(
        max_results=max_results,
        after_date=after_date,
        processed_ids=processed_ids,
    )

    if not emails:
        return {
            "status": "success",
            "emails_fetched": 0,
            "movements_detected": 0,
            "movements_stored": 0,
            "details": [],
        }

    # Step 3: Analyze emails with Claude AI
    analysis_results = analyze_emails(emails)

    # Step 4: Store results in database
    movements_stored = 0
    details = []

    for result_item in analysis_results:
        email_id = result_item["email_id"]
        analysis = result_item["analysis"]
        has_movement = analysis.get("has_movement", False)

        # Mark email as processed
        processed_email = ProcessedEmail(
            gmail_message_id=email_id,
            had_movement=has_movement,
        )
        db.add(processed_email)

        if has_movement:
            for mov_data in analysis.get("movements", []):
                amount = _parse_amount(mov_data.get("amount"))
                if amount is None:
                    logger.warning(
                        "Skipping movement with invalid amount in email %s",
                        email_id,
                    )
                    continue

                movement_date = _parse_datetime(mov_data.get("movement_date"))
                if movement_date is None:
                    # Fallback to email date
                    movement_date = _parse_datetime(result_item.get("date"))
                if movement_date is None:
                    movement_date = datetime.now(timezone.utc)

                movement = Movement(
                    type=_parse_movement_type(mov_data.get("type", "expense")),
                    amount=amount,
                    currency=mov_data.get("currency", "MXN"),
                    account=mov_data.get("account"),
                    movement_date=movement_date,
                    concept=mov_data.get("concept"),
                    merchant=mov_data.get("merchant"),
                    status=MovementStatus.PENDING,
                    source_email_id=email_id,
                )
                db.add(movement)
                movements_stored += 1

        details.append(
            {
                "email_id": email_id,
                "subject": result_item["subject"],
                "has_movement": has_movement,
                "movements_count": len(analysis.get("movements", [])),
            }
        )

    await db.commit()

    return {
        "status": "success",
        "emails_fetched": len(emails),
        "movements_detected": sum(1 for d in details if d["has_movement"]),
        "movements_stored": movements_stored,
        "details": details,
    }
