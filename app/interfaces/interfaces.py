from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from uuid import UUID

from app.entities.attachment import AttachmentEntity
from app.entities.company_duty import CompanyDutyEntity
from app.entities.post import PostEntity
from app.entities.rank import RankEntity
from app.entities.task import TaskEntity
from app.entities.user import UserEntity
from app.entities.vigil_enum import VigilEnumEntity


class IScheduleRepository(ABC):
    @abstractmethod
    async def create_vigils_type(self, data: List[VigilEnumEntity]):
        raise NotImplementedError

    @abstractmethod
    async def get_vigils(
        self,
        start_at: datetime,
        end_at: datetime,
        user_ids: List[UUID],
        vigil_ids: List[UUID],
        ignore_id: int = None,
    ):
        raise NotImplementedError

    @abstractmethod
    async def save_responsible_schedule(
        self, responsible: dict, start_date: datetime, end_date: datetime
    ):
        raise NotImplementedError

    @abstractmethod
    async def save_group_control_schedule(
        self,
        group_control_schedule: list,
        start_date: datetime,
        end_date: datetime,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_vigils_type(self, name: List[str] = None):
        raise NotImplementedError

    @abstractmethod
    async def save_vigils_schedule(
        self, vigils_schedule: dict, start_date: datetime, end_date: datetime
    ):
        raise NotImplementedError


class IUserRepository(ABC):
    @abstractmethod
    async def get_duty_users(self, duty_id: UUID) -> List[UserEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_project_users(self, project_id: UUID) -> List[UserEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_superusers(self) -> List[UserEntity] | None:
        raise NotImplementedError

    @abstractmethod
    async def create_posts(self, data: List[PostEntity]) -> List[PostEntity]:
        raise NotImplementedError

    @abstractmethod
    async def create_company_duties(
        self, data: List[CompanyDutyEntity]
    ) -> List[CompanyDutyEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_duties(self, user: UserEntity) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_users_from_ids(self, user_id: List[UUID] = None) -> list:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def save_refresh_token(
        self, user_id: UUID, refresh_token: str
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_refresh_token(self, user_id: UUID) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def create_ranks(self, data: List[RankEntity]) -> List[RankEntity]:
        raise NotImplementedError


class ITaskRepository(ABC):
    @abstractmethod
    async def create_attachment(self, task_id: UUID, path: str, filename: str) -> AttachmentEntity:
        raise NotImplementedError

    @abstractmethod
    async def create(self, task: TaskEntity) -> TaskEntity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task: TaskEntity) -> TaskEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, task: TaskEntity) -> TaskEntity:
        raise NotImplementedError

    @abstractmethod
    async def get(
        self, task_ids: List[UUID], owner_id: UUID
    ) -> List[TaskEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> TaskEntity:
        raise NotImplementedError



