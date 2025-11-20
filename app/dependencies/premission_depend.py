from uuid import UUID

from fastapi import HTTPException

from app.entities.user import UserEntity


async def check_duty_permission(
    duty_id: UUID, user: UserEntity
):
    if user.is_superuser:
        return True

    if not duty_id in [duty.id for duty in user.duties]:
        raise HTTPException(
            status_code=403, detail="You don't have permissions"
        )
    return True

