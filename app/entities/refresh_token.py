from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.entities.base_entity import BaseEntity

@dataclass
class RefreshTokenEntity(BaseEntity):
    id: UUID | None = None
    user_id: UUID | None = None
    token: str | None = None
    created_at: datetime | None = None