
from pydantic import UUID4
from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.summary.models import FileCRUD
from src.summary.schemas import FileOut


class File:
    crud = FileCRUD

    @classmethod
    async def get(cls, session: AsyncSession, file_id: UUID4) -> FileOut:
        return await cls.crud.get(session, "id", file_id)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> FileOut:
        created_fields = dict(**kwargs)
        return await cls.crud.create(session, **created_fields)