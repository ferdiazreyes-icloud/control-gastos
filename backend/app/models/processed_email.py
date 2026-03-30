from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    gmail_message_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    had_movement: Mapped[bool] = mapped_column(Boolean, default=False)
