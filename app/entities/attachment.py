from app.entities.base_entity import BaseEntity
from dataclasses import dataclass
from uuid import UUID

@dataclass
class AttachmentEntity(BaseEntity):
    id: UUID | None = None
    filename: str | None = None
    file_path: str | None = None
    task_id: UUID | None = None