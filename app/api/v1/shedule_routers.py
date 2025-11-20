from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.database import get_session
from app.dependencies.auth_depend import check_auth_dep
from app.dependencies.premission_depend import check_duty_permission
from app.entities.user import UserEntity
from app.exceptions.exceptions import (
    ExcelParsingError,
    UserNotFoundError,
    VigilsTypeNotFound,
)
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.schedule_schema import ReadVigils
from app.services.schedule_service import ScheduleService
from app.services.user_service import UserService

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/vigils")
async def get_vigils(
    params: ReadVigils = Depends(),
    session=Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    service = ScheduleService(ScheduleRepository(session))
    try:
        kwargs = params.model_dump()

        vigils = await service.get_vigils(**kwargs)
        return [vigil.to_dict() for vigil in vigils]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/vigils")
async def upload_vigils(
    file: UploadFile = File(..., description="Excel файл с расписанием"),
    session=Depends(get_session),
    user: UserEntity = Depends(check_auth_dep),
):
    await check_duty_permission(
        duty_id=UUID("180cd959-23d7-4fff-a7b7-da29e73bea9a"),
        user=user,
        session=session,
    )
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Нужно отправить именно файл .xlsx, тот в котором вы создаете "
            "графики нарядов.",
        )
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    ]:
        raise HTTPException(status_code=400, detail="Неверный формат файла")

    schedule_service = ScheduleService(ScheduleRepository(session))
    user_service = UserService(UserRepository(session))
    try:
        file_bytes = await file.read()
        info = await schedule_service.process_vigils_schedule(file_bytes)
        all_users = await user_service.get_users_from_ids()
        await schedule_service.create_vigils(info, all_users)

    except UserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except VigilsTypeNotFound as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExcelParsingError as e:
        raise HTTPException(status_code=400, detail=str(e))
