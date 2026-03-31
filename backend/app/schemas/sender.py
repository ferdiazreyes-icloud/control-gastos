import uuid
from datetime import datetime

from pydantic import BaseModel


class SenderCreate(BaseModel):
    email_pattern: str
    name: str


class SenderResponse(BaseModel):
    id: uuid.UUID
    email_pattern: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SenderSuggestion(BaseModel):
    email_pattern: str
    name: str
    email_count: int
