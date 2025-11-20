from dataclasses import dataclass
from uuid import UUID
from app.entities.base_entity import BaseEntity

@dataclass
class RankEntity(BaseEntity):
    id: UUID | None = None
    name: str | None = None
    short_name: str | None = None