from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from app.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from app.entities.user import UserEntity
    from app.entities.vigil_enum import VigilEnumEntity

@dataclass
class ScheduleVigilEntity(BaseEntity):
    id: UUID | None = None
    date: datetime | None = None

    vigil_id: int | None = None
    vigil: VigilEnumEntity | None = None

    user_id: UUID | None = None
    user: UserEntity | None = None
