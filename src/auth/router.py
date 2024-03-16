import logging
from typing import Mapping

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import exceptions
from fastapi_users.router.common import ErrorCode
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.manager import UserManager, get_user_manager
from src.auth.config import (
    current_user, current_active_user, current_active_verified_user,
    current_superuser
)
from src.auth.logic import Role, UserTokenVerify
from src.auth.dependencies import valid_role_id, valid_token
from src.auth.schemas import RoleResponse, UserCreate, UserRead, UserUpdate
from src.auth.config import auth_backend, fastapi_users
from src.auth.models import User
from src.database import get_async_session
from src.models import get_by_id


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
    user: User = Depends(current_active_verified_user),
) -> list[RoleResponse]:
    return await Role.get_list(session)


@router_roles.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(
    role: Mapping = Depends(valid_role_id),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_verified_user),
) -> None:
    await Role.delete(session, role.id)
    await session.commit()
    logger.warning(f"Role {role.name} deleted by {user.username}")


@router_roles.get(
        "/{role_id}",
)
async def get_role(
    role: Mapping = Depends(valid_role_id),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_verified_user),
) -> RoleResponse:
    return role


@router_auth.get(
    "/accept",
    response_model=UserRead,
)
async def accept(
    request: Request,
    token: Mapping = Depends(valid_token),
    user_manager: UserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session)
) -> UserRead:
    try:
        user = await user_manager.verify(token.token_verify, request)
        await UserTokenVerify.delete(session, token.token_verify)
        await session.commit()
        logger.info(
            f"User {user.username} accepted, token id {token.id} deleted"
        )
        return user
    except (
        exceptions.InvalidVerifyToken, exceptions.UserNotExists
    ):
        logger.warning(
            "Token is invalid or user doesn't exist. "
            f"Token: {token} User {current_user}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    except exceptions.UserAlreadyVerified:
        logger.warning(
            "User is already verified."
            f"User id {token.user_id} token id {token.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )
    except Exception as e:
        logger.exception(e)
        raise e
