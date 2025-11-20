from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID
from typing import TYPE_CHECKING

from app.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from app.entities.user import OnlyUserEntity
    from app.entities.attachment import AttachmentEntity

@dataclass
class TaskEntity(BaseEntity):
    id: UUID | None = None
    text: str | None = None
    owner_id: UUID | None = None
    owner: OnlyUserEntity | None | UUID = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    expired_at: datetime | None = None
    deleted_at: datetime | None = None

    attachments: List[AttachmentEntity] | None = None
    responsible: List[OnlyUserEntity] | None | [UUID] = None

