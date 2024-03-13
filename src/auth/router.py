import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import exceptions
from fastapi_users.router.common import ErrorCode, ErrorModel
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.manager import UserManager, get_user_manager
from src.auth.config import (
    current_user, current_active_user, current_active_verified_user,
    current_superuser
)
from src.auth.logic import Role, UserTokenVerify
from src.database import get_async_session
from src.auth.schemas import RoleResponse, UserCreate, UserRead, UserUpdate
from src.auth.config import auth_backend, fastapi_users

logger = logging.getLogger('root')

router_auth = APIRouter(prefix="/auth", tags=["auth"])
router_users = APIRouter(prefix="/users", tags=["users"])
router_roles = APIRouter(prefix="/roles", tags=["roles"])

router_auth.include_router(
    fastapi_users.get_auth_router(auth_backend)
)
router_auth.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate)
)
router_auth.include_router(
    fastapi_users.get_verify_router(UserRead)
)
router_auth.include_router(
    fastapi_users.get_reset_password_router()
)
router_users.include_router(
    fastapi_users.get_users_router(
        UserRead, UserUpdate, requires_verification=True
    )
)


@router_roles.get("/")
async def get_roles(
    session: AsyncSession = Depends(get_async_session),
    # current_user: UserRead = Depends(current_active_verified_user),
) -> list[RoleResponse]:
    # logger.info(current_user)
    return await Role.get_list(session)


@router_roles.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID4,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(current_superuser),
) -> None:
    await Role.delete(session, role_id)
    await session.commit()


@router_roles.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID4,
    session: AsyncSession = Depends(get_async_session),
) -> RoleResponse:
    return await Role.get(session, role_id)


@router_auth.get(
    "/accept",
    response_model=UserRead,
    name="auth:accept",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.VERIFY_USER_BAD_TOKEN: {
                            "summary": "Bad token, not existing user or"
                            "not the e-mail currently set for the user.",
                            "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                        },
                        ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                            "summary": "The user is already verified.",
                            "value": {
                                "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                            },
                        },
                    }
                }
            },
        }
    },
)
async def accept(
    token: str,
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    try:
        user = await user_manager.verify(token, request)
        return user  # TODO: добавить логирование и подходящий вывод
    # Временный токен удаляется в on_after_verify менеджера
    except (
        exceptions.InvalidVerifyToken, exceptions.UserNotExists
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    except exceptions.UserAlreadyVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )
    except Exception as e:
        print(e)  # TODO: добавить логирование
        raise e
