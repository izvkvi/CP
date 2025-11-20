from sqlalchemy import Column, String, UUID, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.models.association_tables import associate_task_responsibles

from app.models.base_model import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    text = Column(String, nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.now, onupdate=datetime.now)

    expired_at = Column(TIMESTAMP, nullable=True)

    deleted_at = Column(TIMESTAMP, nullable=True)


    owner_user = relationship(
        "User",
        back_populates="owned_tasks",
        foreign_keys=[owner_id],
        lazy="selectin",
    )

    responsible = relationship(
        "User",
        secondary=associate_task_responsibles,
        back_populates="responsible_tasks",
        lazy="selectin",
    )

    attachments = relationship(
        "Attachment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )