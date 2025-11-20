from app.models.base_model import Base
from sqlalchemy import Column, String, UUID, Integer
import uuid

class AutogenerateTasks(Base):
    __tablename__ = "autogenerate_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    text = Column(String, nullable=False)

    cron_day = Column(Integer, nullable=False)
    cron_month = Column(Integer, nullable=False)
    cron_year = Column(Integer, nullable=False)

    cron_day_of_week = Column(Integer, nullable=False)

    days_start_before_cron = Column(Integer, nullable=False)

    # "user", "duty", "project", "invocation"
    responsible_type = Column(String, nullable=False)
    responsible_id = Column(UUID(as_uuid=True), nullable=False)


