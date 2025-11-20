from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.exceptions.exceptions import (
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotFoundError,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import TokenRefreshRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    service = AuthService(repo)

    try:
        access, refresh = await service.login(
            form_data.username, form_data.password
        )
        return TokenResponse(access_token=access, refresh_token=refresh)
    except (InvalidCredentialsError, UserNotFoundError) as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: TokenRefreshRequest, session: AsyncSession = Depends(get_session)
):
    repo = UserRepository(session)
    service = AuthService(repo)

    try:
        access, refresh = await service.refresh_tokens(body.refresh_token)
        return TokenResponse(access_token=access, refresh_token=refresh)
    except InvalidRefreshTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
