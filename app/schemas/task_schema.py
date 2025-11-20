from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TaskCreate(BaseModel):
    text: str
    attachments: Optional[List[str]] = None
    expired_at: Optional[datetime] = None

    @field_validator("expired_at", mode="after")
    def check_date(cls, v):
        if v is None:
            return v
        v = v.replace(tzinfo=None, microsecond=0, second=0, minute=0, hour=0)
        today = datetime.today().replace(
            microsecond=0, second=0, minute=0, hour=0
        )
        if v < today:
            raise ValueError("expired_at must be today or in the future")
        return v


class TaskUpdate(BaseModel):
    text: str
    expected_date: Optional[datetime] = None
    attachments: Optional[List[str]] = None

    @field_validator("expected_date", mode="after")
    def check_date(cls, v):
        if v is None:
            return v
        v = v.replace(tzinfo=None, microsecond=0, second=0, minute=0, hour=0)
        today = datetime.today().replace(
            microsecond=0, second=0, minute=0, hour=0
        )
        if v < today:
            raise ValueError("expected_date must be today or in the future")
        return v

    @field_validator("text", mode="after")
    def check_text(cls, v):
        if v is None:
            return v
        if len(v) == 0:
            raise ValueError("text not be Null")
        return v

class TaskDelete(BaseModel):
    id: UUID
