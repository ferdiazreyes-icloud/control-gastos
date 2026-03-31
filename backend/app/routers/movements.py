import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.database import get_db
from app.models.movement import Movement, MovementStatus
from app.models.tag import Tag
from app.schemas.movement import MovementCreate, MovementResponse, MovementUpdate

router = APIRouter()


@router.get("/", response_model=list[MovementResponse])
async def list_movements(
    status: Optional[MovementStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    category_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """List movements with optional filters."""
    query = select(Movement).order_by(Movement.movement_date.desc())

    if status:
        query = query.where(Movement.status == status)
    if date_from:
        query = query.where(func.date(Movement.movement_date) >= date_from)
    if date_to:
        query = query.where(func.date(Movement.movement_date) <= date_to)
    if category_id:
        query = query.where(Movement.category_id == category_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=MovementResponse, status_code=201)
async def create_movement(data: MovementCreate, db: AsyncSession = Depends(get_db)):
    """Create a new movement."""
    tag_ids = data.tag_ids
    movement_data = data.model_dump(exclude={"tag_ids"})
    movement = Movement(**movement_data)

    if tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        movement.tags = list(result.scalars().all())

    db.add(movement)
    await db.commit()
    await db.refresh(movement)
    return movement


@router.get("/{movement_id}", response_model=MovementResponse)
async def get_movement(movement_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a movement by ID."""
    movement = await db.get(Movement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    return movement


@router.patch("/{movement_id}", response_model=MovementResponse)
async def update_movement(
    movement_id: uuid.UUID,
    data: MovementUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a movement (confirm, edit, or discard)."""
    movement = await db.get(Movement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")

    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    for field, value in update_data.items():
        setattr(movement, field, value)

    if tag_ids is not None:
        result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        movement.tags = list(result.scalars().all())

    await db.commit()
    await db.refresh(movement)
    return movement


@router.delete("/{movement_id}", status_code=204)
async def delete_movement(movement_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a movement."""
    movement = await db.get(Movement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")

    await db.delete(movement)
    await db.commit()


@router.post("/{movement_id}/keep", response_model=MovementResponse)
async def keep_movement(movement_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Keep this movement and discard others in the same duplicate group."""
    movement = await db.get(Movement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    if not movement.duplicate_group_id:
        raise HTTPException(
            status_code=400, detail="Movement is not part of a duplicate group"
        )

    # Confirm this movement
    movement.status = MovementStatus.CONFIRMED
    movement.is_duplicate = False

    # Discard all others in the same group
    result = await db.execute(
        select(Movement).where(
            Movement.duplicate_group_id == movement.duplicate_group_id,
            Movement.id != movement_id,
        )
    )
    for other in result.scalars().all():
        other.status = MovementStatus.DISCARDED
        other.is_duplicate = True

    await db.commit()
    await db.refresh(movement)
    return movement


@router.post("/{movement_id}/not-duplicate", response_model=MovementResponse)
async def mark_not_duplicate(
    movement_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Remove a movement from its duplicate group."""
    movement = await db.get(Movement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")

    movement.duplicate_group_id = None
    movement.is_duplicate = False
    movement.superseded_by_id = None

    await db.commit()
    await db.refresh(movement)
    return movement
