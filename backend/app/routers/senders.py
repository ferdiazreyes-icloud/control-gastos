import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sender_whitelist import SenderWhitelist
from app.schemas.sender import SenderCreate, SenderResponse

router = APIRouter()


@router.get("/", response_model=list[SenderResponse])
async def list_senders(db: AsyncSession = Depends(get_db)):
    """List all sender whitelist entries."""
    result = await db.execute(
        select(SenderWhitelist)
        .where(SenderWhitelist.is_active.is_(True))
        .order_by(SenderWhitelist.name)
    )
    return result.scalars().all()


@router.post("/", response_model=SenderResponse, status_code=201)
async def create_sender(data: SenderCreate, db: AsyncSession = Depends(get_db)):
    """Add a new sender to the whitelist."""
    sender = SenderWhitelist(
        email_pattern=data.email_pattern.strip().lower(),
        name=data.name.strip(),
    )
    db.add(sender)
    await db.commit()
    await db.refresh(sender)
    return sender


@router.delete("/{sender_id}", status_code=204)
async def delete_sender(sender_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Deactivate a sender from the whitelist."""
    sender = await db.get(SenderWhitelist, sender_id)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    sender.is_active = False
    await db.commit()
