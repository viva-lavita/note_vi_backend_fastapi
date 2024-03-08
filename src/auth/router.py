from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import exceptions
from fastapi_users.router.common import ErrorCode, ErrorModel
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.manager import UserManager, get_user_manager
from src.auth.config import current_user
from src.auth.logic import Role, UserTokenVerify
from src.database import commit, get_async_session, async_session
from src.auth.shemas import RoleResponse, UserCreate, UserRead, UserUpdate
from src.auth.config import auth_backend, fastapi_users

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
    session: AsyncSession = Depends(get_async_session)
) -> list[RoleResponse]:
    return await Role.get_list(session)


@router_roles.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID4
) -> None:
    async with async_session() as session:
        async with commit(session) as session:
            await Role.delete(session, role_id)


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
    user_manager:
    UserManager = Depends(get_user_manager)
) -> UserRead:
    async with async_session() as session:
        async with commit(session) as session:
            try:
                user = await user_manager.verify(token, request)
                await UserTokenVerify.delete(session, user_id=user.id)
                return user  # TODO: добавить логирование и подходящий вывод
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
