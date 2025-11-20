from typing import Literal, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.dependencies.auth_depend import check_auth_dep
from app.dependencies.premission_depend import check_duty_permission
from app.entities.attachment import AttachmentEntity
from app.entities.task import TaskEntity
from app.entities.user import UserEntity
from app.exceptions.exceptions import ResponsibleTypeError, UserNotFoundError
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.task_schema import TaskCreate, TaskDelete, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/")
async def task_create(
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    service = TaskService(TaskRepository(session), UserRepository(session))
    try:
        task = await service.create(
            responsible_id=user.id,
            text=data.text,
            owner_id=user.id,
            responsible_type="user",
            attachments=data.attachments,
            expired_at=data.expired_at,
        )
    except ResponsibleTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    task_map = task.to_dict()
    return {"task": task_map, "detail": "Task created successfully"}


@router.post("/{responsible_type}/{responsible_id}/create")
async def user_task_create(
    data: TaskCreate,
    responsible_type: Literal["user", "duty", "project"] = Path(
        ..., description="Тип ответственного: 'user', 'duty', 'project'"
    ),
    responsible_id: UUID = Path(
        ...,
        description="ID ответственного (пользователь или группа по обязанности)",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    if not user.is_superuser:
        raise HTTPException(status_code=404, detail="You not have permissions to create task for users")

    service = TaskService(TaskRepository(session), UserRepository(session))
    try:
        task = await service.create(
            responsible_id=responsible_id,
            text=data.text,
            owner_id=user.id,
            responsible_type=responsible_type,
            attachments=[AttachmentEntity(file_path=att) for att in data.attachments] if data.attachments else [],
            expired_at=data.expired_at,
        )
    except ResponsibleTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    task_map = task.to_dict()
    return {"task": task_map, "detail": "Task created successfully"}



@router.get("/")
async def task_get(
    ids: Optional[List[str]] = Query(None),
    session: AsyncSession = Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    service = TaskService(TaskRepository(session), UserRepository(session))
    tasks = await service.get(ids=ids, user_id=None if user.is_superuser else user.id)
    return [task.to_dict() for task in tasks]



@router.get("/{user_id}")
async def user_tasks_get(
    ids: Optional[List[str]] = Query(None),
    user_id: UUID = Path(..., description="ID пользователя"),
    session: AsyncSession = Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    if not user.is_superuser:
        if user_id != user.id:
            raise HTTPException(status_code=403, detail="You are not have permissions")

    service = TaskService(TaskRepository(session), UserRepository(session))
    tasks = await service.get(ids=ids, user_id=user_id)
    return [task.to_dict() for task in tasks]


@router.delete("/")
async def task_delete(
    data: TaskDelete,
    session: AsyncSession = Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    service = TaskService(TaskRepository(session), UserRepository(session))

    if await service.delete(TaskEntity(id=data.id)):
        return {"detail": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")


@router.patch("/{task_id}")
async def task_update(
    data: TaskUpdate,
    task_id: UUID = Path(..., description="ID задачи"),
    session: AsyncSession = Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    if not user.is_superuser:
        if task_id not in user.owner_tasks:
            raise HTTPException(status_code=404, detail="You are not have permissions")

    service = TaskService(TaskRepository(session), UserRepository(session))

    task = TaskEntity(
        id=task_id,
        text=data.text if data.text else None,
        expired_at=data.expected_date if data.expected_date else None,
        attachments=[AttachmentEntity(file_path=att) for att in data.attachments] if data.attachments else []
    )

    task = await service.update(task)
    task_map = task.to_dict()
    return {"task": task_map, "detail": "Task updated successfully"}



