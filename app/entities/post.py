from app.entities.base_entity import BaseEntity
from uuid import UUID

from dataclasses import dataclass

@dataclass
class PostEntity(BaseEntity):
    id: UUID | None = None
    name: str | None = None
