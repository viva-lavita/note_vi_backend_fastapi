from datetime import datetime
from pydantic import UUID4
from sqlalchemy import UUID, select

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import RoleNotFoundError
from src.auth.models import Role as RoleModel, RoleCRUD
from src.auth.shemas import RoleResponse
from src.exceptions import ObjectNotFoundError
from src.models import get_list


class Role:
    crud = RoleCRUD

    @classmethod
    async def get(cls, session: AsyncSession, role_id: UUID4) -> RoleResponse:
        try:
            return await cls.crud.get(session, "id", role_id)
        except ObjectNotFoundError:
            raise RoleNotFoundError

    # @classmethod
    # async def create(cls, session: AsyncSession, **kwargs) -> RoleResponse:
    #     created_fields = dict(created_at=datetime.utcnow(), **kwargs)

    #     account = await cls.crud.create(session, **created_fields)

    #     return account

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
