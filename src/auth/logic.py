from datetime import datetime
import logging
from pydantic import UUID4
from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import Role as RoleModel, RoleCRUD, UserCRUD, UserTokenVerifyCRUD
from src.auth.schemas import RoleResponse
from src.exceptions import ObjectNotFoundError
from src.models import get_list, get_by_name


logger = logging.getLogger('root')


class Role:
    crud = RoleCRUD

    @classmethod
    async def get(cls, session: AsyncSession, role_id: UUID4) -> RoleResponse:
        return await cls.crud.get(session, "id", role_id)

    # @classmethod
    # async def create(cls, session: AsyncSession, **kwargs) -> RoleResponse:
    #     created_fields = dict(created_at=datetime.utcnow(), **kwargs)

    #     role = await cls.crud.create(session, **created_fields)

    #     return role

    @classmethod
    async def delete(cls, session: AsyncSession, role_id: UUID4) -> None:
        await cls.crud.delete(session, "id", role_id)

    @classmethod
    async def update(
        cls, session: AsyncSession, role_id: UUID4, **kwargs
    ) -> RoleResponse:
        return await cls.crud.update(session, "id", role_id, **kwargs)

    @classmethod
    async def get_list(cls, session: AsyncSession) -> list[RoleResponse]:
        return await get_list(session, select(RoleModel))

    @classmethod
    async def get_or_create(
        cls, session: AsyncSession, name: str, permission: str
    ) -> RoleResponse:
        role = await get_by_name(session, RoleModel, name)
        if role is None:
            return await cls.crud.create(
                session, name=name, permission=permission
            )
        return role


class UserTokenVerify:
    crud = UserTokenVerifyCRUD

    @classmethod
    async def get(
        cls, session: AsyncSession, token_verify: str
    ) -> UserTokenVerifyCRUD:
        return await cls.crud.get(session, "token_verify", token_verify)

    @classmethod
    async def delete(cls, session: AsyncSession, token_verify: str) -> None:
        await cls.crud.delete(session, "token_verify", token_verify)

    @classmethod
    async def get_or_create(
        cls, session: AsyncSession, user_id: UUID4, token_verify: str
    ) -> UserTokenVerifyCRUD:
        try:
            instance = await cls.crud.get(session, "user_id", user_id)
            instance.token_verify = token_verify
            updated_fields = dict(token_verify=token_verify)
            return await cls.crud.update(
                session, "user_id", user_id, **updated_fields
            )
        except ObjectNotFoundError:
            created_fields = dict(user_id=user_id, token_verify=token_verify)  # Можно добавить еще полей
            return await cls.crud.create(session, **created_fields)


class User:
    crud = UserCRUD

    @classmethod
    async def get(cls, session: AsyncSession, field: str, value) -> UserCRUD:
        return await cls.crud.get(session, field, value)

    # @classmethod
    # async def get_list(cls, session: AsyncSession, field: str, value) -> UserCRUD:
    #     query = select(UserCRUD.table).where(getattr(UserCRUD.table, field) == value)
    #     return await get_list(session, query)