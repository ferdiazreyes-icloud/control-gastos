from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.processed_email import ProcessedEmail
from app.services.gmail import fetch_emails, is_authenticated

router = APIRouter()


@router.get("/status")
async def email_status(db: AsyncSession = Depends(get_db)):
    """Check email ingestion status."""
    result = await db.execute(
        select(ProcessedEmail).order_by(ProcessedEmail.processed_at.desc()).limit(1)
    )
    last_processed = result.scalar_one_or_none()

    total_result = await db.execute(select(ProcessedEmail))
    total = len(total_result.scalars().all())

    return {
        "gmail_connected": is_authenticated(),
        "total_processed": total,
        "last_processed_at": (
            last_processed.processed_at.isoformat() if last_processed else None
        ),
    }


@router.post("/fetch")
async def fetch_new_emails(
    max_results: int = 50,
    after_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch new emails from Gmail.

    Returns the raw emails (not yet analyzed by AI).
    Skips emails that have already been processed.
    """
    if not is_authenticated():
        return {
            "status": "error",
            "message": "Gmail not connected. Go to /auth/login first.",
        }

    # Get already processed email IDs
    result = await db.execute(select(ProcessedEmail.gmail_message_id))
    processed_ids = {row[0] for row in result.all()}

    # Fetch new emails from Gmail
    emails = fetch_emails(
        max_results=max_results,
        after_date=after_date,
        processed_ids=processed_ids,
    )

    return {
        "status": "success",
        "emails_fetched": len(emails),
        "already_processed": len(processed_ids),
        "emails": emails,
    }
