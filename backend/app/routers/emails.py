from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.processed_email import ProcessedEmail
from app.services.gmail import fetch_emails, is_authenticated
from app.services.pipeline import process_emails

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
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch new emails from Gmail inbox (raw, without AI analysis).

    Paginates through all inbox emails matching sender whitelist.
    Useful for previewing what emails will be processed.
    """
    if not is_authenticated():
        return {
            "status": "error",
            "message": "Gmail not connected. Go to /auth/login first.",
        }

    result = await db.execute(select(ProcessedEmail.gmail_message_id))
    processed_ids = {row[0] for row in result.all()}

    emails, _stale_ids = fetch_emails(
        processed_ids=processed_ids,
    )

    return {
        "status": "success",
        "emails_fetched": len(emails),
        "already_processed": len(processed_ids),
        "emails": emails,
    }


@router.post("/process")
async def process_new_emails(
    db: AsyncSession = Depends(get_db),
):
    """
    Full pipeline: fetch inbox emails → analyze with AI → store → archive.

    This is the main endpoint that does everything:
    1. Paginates through ALL inbox emails matching sender whitelist
    2. Sends them to Claude AI for analysis
    3. Stores detected movements in the database as "pending"
    4. Archives processed emails from Gmail inbox
    5. Skips already-processed emails (tracked in processed_emails table)
    """
    if not is_authenticated():
        return {
            "status": "error",
            "message": "Gmail not connected. Go to /auth/login first.",
        }

    result = await process_emails(db=db)

    return result
