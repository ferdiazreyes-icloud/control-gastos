import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.movement import MovementStatus, MovementType
from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse


class MovementCreate(BaseModel):
    type: MovementType = MovementType.EXPENSE
    amount: Decimal
    currency: str = "MXN"
    account: Optional[str] = None
    movement_date: datetime
    concept: Optional[str] = None
    merchant: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    tag_ids: list[uuid.UUID] = []
    notes: Optional[str] = None
    source_email_id: Optional[str] = None


class MovementUpdate(BaseModel):
    type: Optional[MovementType] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    account: Optional[str] = None
    movement_date: Optional[datetime] = None
    concept: Optional[str] = None
    merchant: Optional[str] = None
    status: Optional[MovementStatus] = None
    category_id: Optional[uuid.UUID] = None
    tag_ids: Optional[list[uuid.UUID]] = None
    notes: Optional[str] = None


class MovementResponse(BaseModel):
    id: uuid.UUID
    type: MovementType
    amount: Decimal
    currency: str
    account: Optional[str]
    movement_date: datetime
    concept: Optional[str]
    merchant: Optional[str]
    status: MovementStatus
    notes: Optional[str]
    source_email_id: Optional[str]
    duplicate_group_id: Optional[uuid.UUID]
    is_duplicate: bool
    superseded_by_id: Optional[uuid.UUID]
    category: Optional[CategoryResponse]
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
