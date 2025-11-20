from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_session
from app.entities.user import UserEntity
from app.exceptions.exceptions import UserAlreadyExistsError
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService
from app.dependencies.auth_depend import check_auth_dep

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
async def register(user_data: UserCreate, session=Depends(get_session)):
    service = UserService(UserRepository(session))
    try:
        user_ent = UserEntity(
            username=user_data.username,
            hashed_password=user_data.password,
            name=user_data.name,
            surname=user_data.surname,
            second_name=user_data.second_name,
            invocation=user_data.invocation,
            rank_id=user_data.rank_id,
            post_id=user_data.post_id,
        )

        user = await service.create(user_ent)
        user_map = user.to_dict()
        user_map.pop("hashed_password")
        return {"user": user_map, "detail": "User created successfully"}
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get(
        ids: Optional[List[UUID]]=Query(default=None),
        invocations: Optional[List[str]] = Query(default=None),
        is_deleted: Optional[bool] = Query(default=False),
        post_ids: Optional[List[UUID]] = Query(default=None),
        rank_ids: Optional[List[UUID]] = Query(default=None),
        duties_ids: Optional[List[UUID]] = Query(default=None),
        projects_ids: Optional[List[UUID]] = Query(default=None),
        session=Depends(get_session),
        user: UserEntity = Depends(check_auth_dep)):
    service = UserService(UserRepository(session))
    users = await service.get(
        ids=ids,
        invocations=invocations,
        is_deleted=is_deleted,
        post_ids=post_ids,
        rank_ids=rank_ids,
        duties_ids=duties_ids,
        projects_ids=projects_ids,
    )
    return [user.to_dict() for user in users]


