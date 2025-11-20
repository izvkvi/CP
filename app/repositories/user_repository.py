from typing import List
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.entities.post import PostEntity
from app.entities.project import ProjectEntity
from app.entities.rank import RankEntity
from app.entities.task import TaskEntity
from app.entities.user import UserEntity
from app.entities.company_duty import CompanyDutyEntity
from app.exceptions.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.interfaces.interfaces import IUserRepository
from app.models import Project
from app.models.posts_model import Post
from app.models.refresh_token_model import RefreshToken
from app.models.user_model import User
from app.models.company_duty_model import CompanyDuty
from app.models.ranks_model import Rank
from app.logger.logger import logger


class UserRepository(IUserRepository):
    def __init__(self, session):
        self.session = session

    async def get(self,
                  ids: List[UUID],
                  invocations: List[str],
                  is_deleted: bool,
                  post_ids: List[UUID],
                  rank_ids: List[UUID],
                  duties_ids: List[UUID],
                  projects_ids: List[UUID]
                  ) -> List[UserEntity]:

        stmt = select(User).options(
            selectinload(User.rank),
            selectinload(User.post),
            selectinload(User.duties),
            selectinload(User.projects)
        )

        if ids:
            stmt = stmt.where(User.id.in_(ids))

        if invocations:
            stmt = stmt.where(User.invocation.in_(invocations))

        if not is_deleted:
            stmt = stmt.where(or_(User.is_deleted.is_(False), User.is_deleted.is_(None)))

        if post_ids:
            stmt = stmt.where(User.post_id.in_(post_ids))

        if rank_ids:
            stmt = stmt.where(User.rank_id.in_(rank_ids))

        if duties_ids:
            stmt = stmt.where(User.duties.any(CompanyDuty.id.in_(duties_ids)))

        if projects_ids:
            stmt = stmt.where(User.projects.any(Project.id.in_(projects_ids)))

        results = (await self.session.execute(stmt)).scalars().all()

        return [UserEntity(
            id=result.id,
            username=result.username,
            name=result.name,
            surname=result.surname,
            second_name=result.second_name,
            short_name=result.short_name,
            short_name_2=result.short_name_2,
            invocation=result.invocation,
            hashed_password=result.hashed_password,
            is_superuser=result.is_superuser,
            is_deleted=result.is_deleted,
            register_at=result.register_at,
            post_id=result.post_id,
            rank_id=result.rank_id,
            duties=[CompanyDutyEntity(id=duty.id) for duty in result.duties],
            projects=[ProjectEntity(id=project.id) for project in result.projects],
        ) for result in results]

    async def get_superusers(self) -> list[UserEntity] | None:
        stmt = select(User).where(User.is_superuser == True, User.is_deleted == False)
        result = (await self.session.execute(stmt)).scalars().all()
        return (
            [
                UserEntity(
                    id=user.id,
                    username=user.username,
                    name=user.name,
                    surname=user.surname,
                    second_name=user.second_name,
                    short_name=user.short_name,
                    short_name_2=user.short_name_2,
                    invocation=user.invocation,
                    hashed_password=user.hashed_password,
                    is_superuser=user.is_superuser,
                    is_deleted=user.is_deleted,
                    register_at=user.register_at,
                    post_id=user.post_id,
                    rank_id=user.rank_id) for user in result]
            if result
            else None
        )

    async def create_ranks(self, data: List[RankEntity]) -> List[RankEntity]:
        if not data:
            return []

        ranks_orm = [Rank(**d.to_dict()) for d in data]
        self.session.add_all(ranks_orm)
        await self.session.commit()
        return [RankEntity(
            id=d.id,
            name=d.name,
            short_name=d.short_name,
        ) for d in ranks_orm]

    async def create_posts(self, data: List[PostEntity]) -> List[PostEntity]:
        if not data:
            return []

        post_orm = [Post(**d.to_dict()) for d in data]
        self.session.add_all(post_orm)
        await self.session.commit()
        return [PostEntity(
            id=d.id,
            name=d.name,
        ) for d in post_orm]

    async def get_users_from_ids(
        self, user_id: List[UUID] = None
    ) -> list[UserEntity]:
        stmt = select(User).options(
            selectinload(User.rank),
            selectinload(User.post),
            selectinload(User.duties),
            selectinload(User.projects),
            selectinload(User.responsible_tasks),
        )
        if user_id:
            stmt = stmt.where(User.id.in_(user_id))
        result = (await self.session.execute(stmt)).scalars().all()
        return [UserEntity(
            id=user.id,
            username=user.username,
            name=user.name,
            surname=user.surname,
            second_name=user.second_name,
            short_name=user.short_name,
            short_name_2=user.short_name_2,
            invocation=user.invocation,
            hashed_password=user.hashed_password,
            is_superuser=user.is_superuser,
            is_deleted=user.is_deleted,
            register_at=user.register_at,
            post_id=user.post_id,
            rank_id=user.rank_id,
            duties=[CompanyDutyEntity(id=duty.id)for duty in user.duties],
            projects=[ProjectEntity(id=project.id)for project in user.projects],
            owner_tasks=[TaskEntity(id=task.id)for task in user.owned_tasks],
            responsible_tasks=[TaskEntity(id=task.id)for task in user.responsible_tasks]) for user in result]

    async def create_company_duties(
        self, data: List[CompanyDutyEntity]
    ) -> List[CompanyDutyEntity]:
        if not data:
            return []
        company_duties = [CompanyDuty(**d.to_dict()) for d in data]
        self.session.add_all(company_duties)
        await self.session.commit()
        return [CompanyDutyEntity(
            id=d.id,
            name=d.name,
        ) for d in company_duties]

    async def get_user_duties(self, user: UserEntity) -> UserEntity:
        stmt = (
            select(User)
            .options(selectinload(User.duties))
            .where(User.id == user.id)
        )
        result = (await self.session.execute(stmt)).scalar_one_or_none()

        if not result:
            raise UserNotFoundError(f"User with id '{user.id}' not found")

        duties_entities = [
            CompanyDutyEntity(
                id=duty.id,
                name=duty.name,
            ) for duty in result.duties
        ]

        user.duties = duties_entities
        return user

    async def get_by_id(self, user_id: UUID) -> UserEntity:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.rank),
                selectinload(User.post),
                selectinload(User.duties),
                selectinload(User.projects),
                selectinload(User.responsible_tasks),
            )
        )
        result = (await self.session.execute(stmt)).scalar_one_or_none()

        if not result:
            raise UserNotFoundError(f"User with id '{str(user_id)}' not found")

        return UserEntity(
            id=result.id,
            username=result.username,
            name=result.name,
            surname=result.surname,
            second_name=result.second_name,
            short_name=result.short_name,
            short_name_2=result.short_name_2,
            invocation=result.invocation,
            hashed_password=result.hashed_password,
            is_superuser=result.is_superuser,
            is_deleted=result.is_deleted,
            register_at=result.register_at,
            post_id=result.post_id,
            rank_id=result.rank_id,
            duties=[CompanyDutyEntity(id=duty.id)for duty in result.duties],
            projects=[ProjectEntity(id=project.id)for project in result.projects],
            owner_tasks=[TaskEntity(id=task.id)for task in result.owned_tasks],
            responsible_tasks=[TaskEntity(id=task.id)for task in result.responsible_tasks])

    async def create(self, user: UserEntity) -> UserEntity:
        user_orm = User(**user.to_dict())
        self.session.add(user_orm)

        try:
            await self.session.flush()

            stmt = (
                select(User)
                .options(
                    selectinload(User.post),
                    selectinload(User.rank)
                )
                .where(User.id == user_orm.id)
            )
            result = (await self.session.execute(stmt)).scalars().first()

            await self.session.commit()

            return UserEntity(
                id=result.id,
                username=result.username,
                name=result.name,
                surname=result.surname,
                second_name=result.second_name,
                short_name=result.short_name,
                short_name_2=result.short_name_2,
                invocation=result.invocation,
                hashed_password=result.hashed_password,
                is_superuser=result.is_superuser,
                is_deleted=result.is_deleted,
                register_at=result.register_at,
                post_id=result.post_id,
                post=PostEntity(
                    id=result.post.id,
                    name=result.post.name
                ) if result.post else None,
                rank_id=result.rank_id,
                rank=RankEntity(
                    id=result.rank.id,
                    name=result.rank.name,
                    short_name=result.rank.short_name,
                ) if result.rank else None,
            )

        except IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            raise UserAlreadyExistsError(f"User '{user.username}' already exists")

    async def save_refresh_token(self, user_id: UUID, refresh_token: str):
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        existing = (await self.session.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.token = refresh_token
        else:
            self.session.add(
                RefreshToken(user_id=user_id, token=refresh_token)
            )

        await self.session.commit()

    async def get_refresh_token(self, user_id: UUID) -> str | None:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        token_obj = (await self.session.execute(stmt)).scalar_one_or_none()
        return token_obj.token if token_obj else None

    async def get_by_username(self, username: str) -> UserEntity | None:
        stmt = (
            select(User)
            .where(User.username == username)
            .options(
                selectinload(User.rank),
                selectinload(User.post),
                selectinload(User.duties),
                selectinload(User.projects),
                selectinload(User.responsible_tasks),
            )
        )
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if not user:
            return None

        return UserEntity(
            id=user.id,
            username=user.username,
            name=user.name,
            surname=user.surname,
            second_name=user.second_name,
            short_name=user.short_name,
            short_name_2=user.short_name_2,
            invocation=user.invocation,
            hashed_password=user.hashed_password,
            is_superuser=user.is_superuser,
            is_deleted=user.is_deleted,
            register_at=user.register_at,
            post_id=user.post_id,
            rank_id=user.rank_id,
            duties=[CompanyDutyEntity(id=duty.id)for duty in user.duties],
            projects=[ProjectEntity(id=project.id)for project in user.projects],
            owner_tasks=[TaskEntity(id=task.id)for task in user.owned_tasks],
            responsible_tasks=[TaskEntity(id=task.id)for task in user.responsible_tasks])

    async def get_duty_users(self, duty_id: UUID) -> List[UserEntity]:
        stmt = (
            select(User)
            .options(
                selectinload(User.duties),
                selectinload(User.rank),
                selectinload(User.post),
                selectinload(User.projects),
                selectinload(User.responsible_tasks),
            )
            .where(User.duties.any(CompanyDuty.id == duty_id))
        )
        result = (await self.session.execute(stmt)).scalars().all()
        return (
            [UserEntity(
                id=user.id,
                username=user.username,
                name=user.name,
                surname=user.surname,
                second_name=user.second_name,
                short_name=user.short_name,
                short_name_2=user.short_name_2,
                invocation=user.invocation,
                hashed_password=user.hashed_password,
                is_superuser=user.is_superuser,
                is_deleted=user.is_deleted,
                register_at=user.register_at,
                post_id=user.post_id,
                rank_id=user.rank_id,
                duties=[CompanyDutyEntity(id=duty.id) for duty in user.duties],
                projects=[ProjectEntity(id=project.id) for project in user.projects],
                owner_tasks=[TaskEntity(id=task.id) for task in user.owned_tasks],
                responsible_tasks=[TaskEntity(id=task.id) for task in user.responsible_tasks])
            for user in result]
            if result
            else []
        )

    async def get_project_users(self, project_id: UUID) -> List[UserEntity]:
        stmt = (
            select(User)
            .options(
                selectinload(User.duties),
                selectinload(User.rank),
                selectinload(User.post),
                selectinload(User.projects),
                selectinload(User.responsible_tasks),
            )
            .where(User.projects.any(Project.id == project_id))
        )
        result = (await self.session.execute(stmt)).scalars().all()
        return (
            [UserEntity(
                id=user.id,
                username=user.username,
                name=user.name,
                surname=user.surname,
                second_name=user.second_name,
                short_name=user.short_name,
                short_name_2=user.short_name_2,
                invocation=user.invocation,
                hashed_password=user.hashed_password,
                is_superuser=user.is_superuser,
                is_deleted=user.is_deleted,
                register_at=user.register_at,
                post_id=user.post_id,
                rank_id=user.rank_id,
                duties=[CompanyDutyEntity(id=duty.id) for duty in user.duties],
                projects=[ProjectEntity(id=project.id) for project in user.projects],
                owner_tasks=[TaskEntity(id=task.id) for task in user.owned_tasks],
                responsible_tasks=[TaskEntity(id=task.id) for task in user.responsible_tasks])
                for user in result]
            if result
            else []
        )

