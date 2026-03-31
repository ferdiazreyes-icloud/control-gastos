import logging
import uuid
from datetime import timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement, MovementStatus

logger = logging.getLogger(__name__)

# Scoring thresholds
DUPLICATE_THRESHOLD = 60
DATE_WINDOW_HOURS = 48
PROGRESSIVE_AMOUNT_TOLERANCE = 0.20  # 20% tolerance for Uber Eats-style updates
PRE_AUTH_AMOUNTS = {Decimal("1.00"), Decimal("0.01"), Decimal("10.00")}


def _normalize_merchant(merchant: Optional[str]) -> str:
    """Normalize merchant name for comparison."""
    if not merchant:
        return ""
    normalized = merchant.lower().strip()
    # Remove common prefixes from bank descriptions
    for prefix in ["paypal *", "paypal*", "pago *", "pago*"]:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
    return normalized


def _score_match(new: Movement, existing: Movement) -> int:
    """Calculate duplicate score between two movements."""
    score = 0

    # Exact amount match (+40)
    if new.amount == existing.amount:
        score += 40

    # Merchant matching
    new_merchant = _normalize_merchant(new.merchant)
    existing_merchant = _normalize_merchant(existing.merchant)

    if new_merchant and existing_merchant:
        if new_merchant == existing_merchant:
            # Exact match (+30)
            score += 30
        elif new_merchant in existing_merchant or existing_merchant in new_merchant:
            # Substring match (+20)
            score += 20

    # Date within window (+15)
    if new.movement_date and existing.movement_date:
        # Normalize both to UTC-aware for comparison
        new_date = new.movement_date
        existing_date = existing.movement_date
        if new_date.tzinfo is None:
            new_date = new_date.replace(tzinfo=timezone.utc)
        if existing_date.tzinfo is None:
            existing_date = existing_date.replace(tzinfo=timezone.utc)
        time_diff = abs(new_date - existing_date)
        if time_diff <= timedelta(hours=DATE_WINDOW_HOURS):
            score += 15

    # Same account (+10)
    if new.account and existing.account:
        if new.account.lower() == existing.account.lower():
            score += 10

    return score


def _is_pre_auth(movement: Movement) -> bool:
    """Check if a movement looks like a pre-authorization hold."""
    return movement.amount in PRE_AUTH_AMOUNTS


def _is_progressive_update(new: Movement, existing: Movement) -> bool:
    """Check if new movement is a progressive update of existing (e.g., Uber Eats)."""
    new_merchant = _normalize_merchant(new.merchant)
    existing_merchant = _normalize_merchant(existing.merchant)

    if not new_merchant or not existing_merchant:
        return False

    # Must be same or similar merchant
    merchant_match = (
        new_merchant == existing_merchant
        or new_merchant in existing_merchant
        or existing_merchant in new_merchant
    )
    if not merchant_match:
        return False

    # Must be within 24 hours
    if new.movement_date and existing.movement_date:
        new_date = new.movement_date
        existing_date = existing.movement_date
        if new_date.tzinfo is None:
            new_date = new_date.replace(tzinfo=timezone.utc)
        if existing_date.tzinfo is None:
            existing_date = existing_date.replace(tzinfo=timezone.utc)
        time_diff = abs(new_date - existing_date)
        if time_diff > timedelta(hours=24):
            return False

    # Amount within tolerance
    if existing.amount > 0:
        diff_ratio = abs(float(new.amount - existing.amount)) / float(existing.amount)
        if diff_ratio <= PROGRESSIVE_AMOUNT_TOLERANCE:
            return True

    return False


async def check_duplicates(
    new_movement: Movement,
    db: AsyncSession,
) -> Optional[uuid.UUID]:
    """
    Check if a new movement is a duplicate of an existing one.

    Returns:
        The duplicate_group_id if a match is found, None otherwise.
        Also mutates new_movement.is_duplicate and sets superseded_by_id
        on existing movements when appropriate.
    """
    # Query recent movements (7 days, same currency, pending or confirmed)
    mov_date = new_movement.movement_date
    if mov_date.tzinfo is None:
        mov_date = mov_date.replace(tzinfo=timezone.utc)
    cutoff_date = mov_date - timedelta(days=7)
    result = await db.execute(
        select(Movement).where(
            Movement.currency == new_movement.currency,
            Movement.movement_date >= cutoff_date,
            Movement.status.in_([MovementStatus.PENDING, MovementStatus.CONFIRMED]),
        )
    )
    recent_movements = result.scalars().all()

    best_match: Optional[Movement] = None
    best_score = 0

    for existing in recent_movements:
        score = _score_match(new_movement, existing)

        if score >= DUPLICATE_THRESHOLD and score > best_score:
            best_match = existing
            best_score = score

    if not best_match:
        return None

    logger.info(
        "Duplicate detected (score=%d): '%s' $%s matches '%s' $%s",
        best_score,
        new_movement.merchant,
        new_movement.amount,
        best_match.merchant,
        best_match.amount,
    )

    # Determine or reuse duplicate group ID
    group_id = best_match.duplicate_group_id or uuid.uuid4()

    # Mark best_match with group if not already
    if not best_match.duplicate_group_id:
        best_match.duplicate_group_id = group_id

    # Handle pre-auth: old one is superseded by new
    if _is_pre_auth(best_match):
        best_match.superseded_by_id = new_movement.id
        best_match.is_duplicate = True

    # Handle progressive updates: old superseded by new
    if _is_progressive_update(new_movement, best_match):
        best_match.superseded_by_id = new_movement.id
        best_match.is_duplicate = True

    # Mark new movement as duplicate
    new_movement.duplicate_group_id = group_id
    new_movement.is_duplicate = True

    return group_id
