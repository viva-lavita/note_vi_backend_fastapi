from datetime import datetime
import logging
from pydantic import UUID4
from sqlalchemy import UUID, select

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import RoleNotFoundError
from src.auth.models import Role as RoleModel, RoleCRUD, UserTokenVerifyCRUD
from src.auth.schemas import RoleResponse
from src.exceptions import ObjectNotFoundError
from src.models import get_list


logger = logging.getLogger('root')


class Role:
    crud = RoleCRUD

    @classmethod
    async def get(cls, session: AsyncSession, role_id: UUID4) -> RoleResponse:
        try:
            return await cls.crud.get(session, "id", role_id)
        except ObjectNotFoundError:
            logger.warning(f"Role with id {role_id} not found")
            return None
        except Exception as e:
            logger.exception(e)
            return None

    # @classmethod
    # async def create(cls, session: AsyncSession, **kwargs) -> RoleResponse:
    #     created_fields = dict(created_at=datetime.utcnow(), **kwargs)

    #     account = await cls.crud.create(session, **created_fields)

    #     return account

    @classmethod
    async def delete(cls, session: AsyncSession, role_id: UUID4) -> None:
        try:
            await cls.crud.get(session, "id", role_id)
        except ObjectNotFoundError:
            logger.warning(f"Role with id {role_id} not found")
            raise RoleNotFoundError
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise
        await cls.crud.delete(session, "id", role_id)

    @classmethod
    async def update(
        cls, session: AsyncSession, role_id: UUID4, **kwargs
    ) -> RoleResponse:
        return await cls.crud.update(session, "id", role_id, **kwargs)

    @classmethod
    async def get_list(cls, session: AsyncSession) -> list[RoleResponse]:
        return await get_list(session, select(RoleModel))


class UserTokenVerify:
    crud = UserTokenVerifyCRUD

    @classmethod
    async def get(
        cls, session: AsyncSession, token_verify: str
    ) -> UserTokenVerifyCRUD:
        try:
            return await cls.crud.get(session, "token_verify", token_verify)
        except ObjectNotFoundError:
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID4) -> None:
        await cls.crud.delete(session, "user_id", user_id)

    @classmethod
    async def create(
        cls, session: AsyncSession, user_id: UUID4, token_verify: str
    ) -> UserTokenVerifyCRUD:
        created_fields = dict(user_id=user_id, token_verify=token_verify)
        return await cls.crud.create(session, **created_fields)
