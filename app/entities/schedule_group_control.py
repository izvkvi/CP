from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.entities.base_entity import BaseEntity

@dataclass
class ScheduleGroupControlEntity(BaseEntity):
    id: UUID | None = None
    date: datetime | None = None