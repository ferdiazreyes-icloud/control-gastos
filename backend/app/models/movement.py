import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MovementType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class MovementStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISCARDED = "discarded"


class Movement(Base):
    __tablename__ = "movements"

    type: Mapped[MovementType] = mapped_column(
        Enum(MovementType), nullable=False, default=MovementType.EXPENSE
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")
    account: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    concept: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    merchant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[MovementStatus] = mapped_column(
        Enum(MovementStatus), nullable=False, default=MovementStatus.PENDING
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_email_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )
    category: Mapped[Optional["Category"]] = relationship(  # noqa: F821
        "Category", back_populates="movements", lazy="selectin"
    )
    tags: Mapped[list["Tag"]] = relationship(  # noqa: F821
        "Tag", secondary="movement_tags", lazy="selectin"
    )
