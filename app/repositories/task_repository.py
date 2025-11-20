from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import and_

from app.entities.task import TaskEntity
from app.entities.attachment import AttachmentEntity
from app.entities.user import UserEntity, OnlyUserEntity
from app.exceptions.exceptions import TaskNotFound
from app.interfaces.interfaces import ITaskRepository
from app.models import User
from app.models.attachment_model import Attachment
from app.models.task_model import Task


class TaskRepository(ITaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    # TODO СДЕЛАТЬ ВОЗМОЖНОСТЬ ПРИЛОЖИТЬ ФАЙЛЫ К ЗАДАЧЕ ИЗ S3
    async def create_attachment(self, task_id: UUID, path: str, filename: str) -> AttachmentEntity:
        stmt = select(Attachment).where(Attachment.task_id == task_id)
        result = (await self.session.execute(stmt)).scalars().first()
        await self.session.delete(result)

        attachment = Attachment(task_id=task_id, file_path=path, filename=filename)
        self.session.add(attachment)
        await self.session.commit()
        att_ent = AttachmentEntity(
            id=attachment.id,
            task_id=attachment.task_id,
            file_path=attachment.file_path,
            filename=attachment.filename
        )
        return att_ent

    async def create(self, task: TaskEntity) -> TaskEntity:
        stmt = select(User).where(User.id.in_([u.id for u in task.responsible]))
        responsible_users = (await self.session.execute(stmt)).scalars().all()

        task_orm = Task(
            text=task.text,
            owner_id=task.owner_id,
            responsible=responsible_users,
            expired_at=task.expired_at,
        )
        self.session.add(task_orm)
        await self.session.commit()

        stmt = (
            select(Task)
            .options(
                selectinload(Task.owner_user),
                selectinload(Task.responsible)
            )
            .where(Task.id == task_orm.id)
        )
        result = (await self.session.execute(stmt)).scalars().first()
        task_orm = result

        task = TaskEntity(
            id=task_orm.id,
            text=task_orm.text,
            owner=UserEntity(
                id=task_orm.owner_user.id,
                name=task_orm.owner_user.name,
                surname=task_orm.owner_user.surname,
                second_name=task_orm.owner_user.second_name,
                short_name=task_orm.owner_user.short_name,
                short_name_2=task_orm.owner_user.short_name_2,
                rank_id=task_orm.owner_user.rank_id,
                post_id=task_orm.owner_user.post_id,
            ),
            responsible=[UserEntity(
                id=u.id,
                name=u.name,
                surname=u.surname,
                second_name=u.second_name,
                short_name=u.short_name,
                short_name_2=u.short_name_2,
                rank_id=u.rank_id,
                post_id=u.post_id,
            ) for u in task_orm.responsible],
            expired_at=task_orm.expired_at,
            created_at=task_orm.created_at,
            updated_at=task_orm.updated_at
        )
        return task

    # TODO СДЕЛАТЬ ВОЗМОЖНОСТЬ ПРИЛОЖИТЬ ФАЙЛЫ К ЗАДАЧЕ ИЗ S3
    async def update(self, task: TaskEntity) -> TaskEntity:
        stmt = (
            select(Task)
            .where(
                and_(
                    Task.id == task.id,
                    Task.deleted_at.is_(None)
                )
            )
        )
        result = (await self.session.execute(stmt)).scalars().first()

        if not result:
            raise ValueError("Task not found")

        if task.text is not None:
            if task.text == "":
                raise ValueError("Text can't be empty")
            result.text = task.text

        if task.expired_at is not None:
            result.expired_at = task.expired_at

        await self.session.commit()

        return TaskEntity(
            id=result.id,
            text=result.text,
            owner=UserEntity(
                id=result.owner_user.id,
                name=result.owner_user.name,
                surname=result.owner_user.surname,
                second_name=result.owner_user.second_name,
                short_name=result.owner_user.short_name,
                short_name_2=result.owner_user.short_name_2,
                rank_id=result.owner_user.rank_id,
                post_id=result.owner_user.post_id,
            ),
            responsible=[UserEntity(
                id=u.id,
                name=u.name,
                surname=u.surname,
                second_name=u.second_name,
                short_name=u.short_name,
                short_name_2=u.short_name_2,
                rank_id=u.rank_id,
                post_id=u.post_id,
            ) for u in result.responsible],
            expired_at=result.expired_at,
            created_at=result.created_at,
            updated_at=result.updated_at,
            attachments=[AttachmentEntity(
                id=a.id,
                filename=a.filename,
                file_path=a.file_path,
            ) for a in result.attachments]
        )


    async def delete(self, task: TaskEntity) -> bool:
        stmt = (
            select(Task)
            .where(
                and_(
                    Task.id == task.id,
                    Task.deleted_at.is_(None)
                )
            )
            .options(selectinload(Task.responsible))
        )
        result = (await self.session.execute(stmt)).scalars().first()

        if not result:
            return False

        result.responsible.clear()

        result.deleted_at = datetime.now()

        await self.session.commit()
        return True

    async def get_by_id(self, task_id: UUID) -> TaskEntity:
        stmt = (select(Task).options(
            selectinload(Task.owner_user),
            selectinload(Task.responsible),
            selectinload(Task.attachments),
        )
        .where(Task.id == task_id))
        task_orm = (await self.session.execute(stmt)).scalars().first()

        if not task_orm:
            raise TaskNotFound("Task not found")

        return TaskEntity(
            id=task_orm.id,
            text=task_orm.text,
            owner=UserEntity(
                id=task_orm.owner_user.id,
                name=task_orm.owner_user.name,
                surname=task_orm.owner_user.surname,
                second_name=task_orm.owner_user.second_name,
                short_name=task_orm.owner_user.short_name,
                short_name_2=task_orm.owner_user.short_name_2,
                rank_id=task_orm.owner_user.rank_id,
                post_id=task_orm.owner_user.post_id,
            ),
            responsible=[UserEntity(
                id=u.id,
                name=u.name,
                surname=u.surname,
                second_name=u.second_name,
                short_name=u.short_name,
                short_name_2=u.short_name_2,
                rank_id=u.rank_id,
                post_id=u.post_id,
            ) for u in task_orm.responsible],
            expired_at=task_orm.expired_at,
            created_at=task_orm.created_at,
            updated_at=task_orm.updated_at,
            attachments=[AttachmentEntity(
                id=a.id,
                filename=a.filename,
                file_path=a.file_path,
            ) for a in task_orm.attachments]
        )

    async def get(
        self,
        task_ids: List[UUID] = None,
        responsible_id: UUID = None
    ) -> List[TaskEntity]:

        stmt = select(Task)

        if task_ids:
            stmt.where(Task.id.in_(task_ids))
        if responsible_id:
            stmt.where(Task.responsible.any(User.id == responsible_id))

        result = (await self.session.execute(stmt)).scalars().all()

        return [TaskEntity(
            id=t.id,
            text=t.text,
            owner=UserEntity(
                id=t.owner_user.id,
                name=t.owner_user.name,
                surname=t.owner_user.surname,
                second_name=t.owner_user.second_name,
                short_name=t.owner_user.short_name,
                short_name_2=t.owner_user.short_name_2,
                rank_id=t.owner_user.rank_id,
                post_id=t.owner_user.post_id,
            ),
            responsible=[UserEntity(
                id=u.id,
                name=u.name,
                surname=u.surname,
                second_name=u.second_name,
                short_name=u.short_name,
                short_name_2=u.short_name_2,
                rank_id=u.rank_id,
                post_id=u.post_id,
            ) for u in t.responsible],
            expired_at=t.expired_at,
            created_at=t.created_at,
            updated_at=t.updated_at,
            attachments=[AttachmentEntity(
                id=a.id,
                filename=a.filename,
                file_path=a.file_path,
            ) for a in t.attachments]
        )
                for t in result]