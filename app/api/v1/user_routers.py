from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_session
from app.entities.user import UserEntity
from app.exceptions.exceptions import UserAlreadyExistsError
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService

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
