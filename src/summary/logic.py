from uuid import UUID

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.models import get_list
from src.summary.models import (
    FileCRUD, File as FileModel, SummaryCRUD, Summary as SummaryModel
)
from src.summary.schemas import File as FileSchema, Summary as SummarySchema


class File:
    crud = FileCRUD

    @classmethod
    async def get(cls, session: AsyncSession, file_id: UUID4) -> FileSchema:
        return await cls.crud.get(session, "id", file_id)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> FileSchema:
        created_fields = dict(**kwargs)
        return await cls.crud.create(session, **created_fields)

    @classmethod
    async def get_list_by_username(
          cls, session: AsyncSession, username: str) -> list[FileSchema]:
        query = select(FileModel).join(User).where(User.username == username)
        return await get_list(session, query)

    @classmethod
    async def get_list(cls, session: AsyncSession, user_id: UUID = None) -> list[FileSchema]:
        if user_id is None:
            query = select(FileModel)
        else:
            query = select(FileModel).where(FileModel.user_id == user_id)
        return await get_list(session, query)


class Summary:
    crud = SummaryCRUD

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> SummarySchema:
        created_fields = dict(**kwargs)
        return await cls.crud.create(session, **created_fields)

    @classmethod
    async def get(
          cls, session: AsyncSession, summary_id: UUID4) -> SummarySchema:
        return await cls.crud.get(session, "id", summary_id)

    @classmethod
    async def get_list(
        cls, session: AsyncSession, user_id: UUID | None = None,
        is_public: bool | None = None, username: str | None = None
    ) -> list[SummarySchema]:
        query = select(SummaryModel)
        if user_id:
            query = query.filter(SummaryModel.author_id == user_id)
        if is_public is not None:
            query = query.filter(SummaryModel.is_public == is_public)
        if username:
            query = query.join(User).filter(User.username == username)
        return await get_list(session, query)
