from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy import UUID, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.logic import Role
from src.database import commit, get_async_session, async_session
from src.models import get_list
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
