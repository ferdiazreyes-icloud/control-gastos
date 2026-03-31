import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement, MovementStatus, MovementType
from app.models.processed_email import ProcessedEmail
from app.models.sender_whitelist import SenderWhitelist
from app.services.analyzer import analyze_emails
from app.services.dedup import check_duplicates
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


async def _get_sender_patterns(db: AsyncSession) -> list[str]:
    """Load active sender patterns from the whitelist."""
    result = await db.execute(
        select(SenderWhitelist.email_pattern).where(SenderWhitelist.is_active.is_(True))
    )
    return [row[0] for row in result.all()]


async def _get_last_processed_date(db: AsyncSession) -> Optional[str]:
    """Get the date of the last processed email for auto-dating."""
    result = await db.execute(
        select(ProcessedEmail.processed_at)
        .order_by(ProcessedEmail.processed_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if row:
        return row.strftime("%Y/%m/%d")
    return None


async def process_emails(
    db: AsyncSession,
    max_results: int = 50,
    after_date: Optional[str] = None,
) -> dict:
    """
    Full pipeline: fetch emails → analyze with AI → deduplicate → store.

    Uses sender whitelist to filter Gmail queries.
    Uses auto-date from last processed email if no after_date given.
    Checks for duplicates before storing movements.
    """
    # Step 1: Get already processed email IDs
    result = await db.execute(select(ProcessedEmail.gmail_message_id))
    processed_ids = {row[0] for row in result.all()}

    # Step 2: Load sender whitelist patterns
    sender_patterns = await _get_sender_patterns(db)

    # Step 3: Auto-date if not provided
    if not after_date:
        after_date = await _get_last_processed_date(db)

    # Step 4: Fetch new emails from Gmail (filtered by senders + date)
    emails = fetch_emails(
        max_results=max_results,
        after_date=after_date,
        processed_ids=processed_ids,
        sender_patterns=sender_patterns if sender_patterns else None,
    )

    if not emails:
        return {
            "status": "success",
            "emails_fetched": 0,
            "movements_detected": 0,
            "movements_stored": 0,
            "duplicates_found": 0,
            "details": [],
        }

    # Step 5: Analyze emails with Claude AI
    analysis_results = analyze_emails(emails)

    # Step 6: Store results with deduplication
    movements_stored = 0
    duplicates_found = 0
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
                    source_email_sender=result_item.get("sender", ""),
                    source_email_subject=result_item.get("subject", ""),
                )

                # Check for duplicates before storing
                group_id = await check_duplicates(movement, db)
                if group_id:
                    duplicates_found += 1

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
        "duplicates_found": duplicates_found,
        "details": details,
    }
