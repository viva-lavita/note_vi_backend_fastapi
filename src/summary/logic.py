from uuid import UUID

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.models import get_list
from src.summary.models import (
    FileCRUD, File as FileModel, SummaryCRUD, Summary as SummaryModel,
    SummaryImageCRUD, SummaryImage as SummaryImageModel
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
    async def create(cls, session: AsyncSession, **kwargs) -> SummaryModel:
        created_fields = dict(**kwargs)
        return await cls.crud.create(session, **created_fields)

    @classmethod
    async def get(
          cls, session: AsyncSession, summary_id: UUID4) -> SummaryModel:
        return await cls.crud.get(session, "id", summary_id)

    @classmethod
    async def get_list(
        cls, session: AsyncSession, user_id: UUID | None = None,
        is_public: bool | None = None, username: str | None = None
    ) -> list[SummaryModel]:
        query = select(SummaryModel).order_by(SummaryModel.created_at.desc())
        if user_id:
            query = query.filter(SummaryModel.author_id == user_id)
        if is_public is not None:
            query = query.filter(SummaryModel.is_public == is_public)
        if username:
            query = query.join(User).filter(User.username == username)
        return await get_list(session, query)

    @classmethod
    async def delete(cls, session: AsyncSession, summary_id: UUID4) -> None:
        await cls.crud.delete(session, "id", summary_id)

    @classmethod
    async def update(
        cls, session: AsyncSession, summary_id: UUID4, new_summary
    ) -> None:
        updated_fields = new_summary.model_dump(exclude_unset=True)
        updated_fields["name"] = updated_fields["name"] + ".md"
        return await cls.crud.update(
            session, "id", summary_id, **updated_fields)

    # @classmethod
    # async def add_image(cls, session: AsyncSession, summary_id: UUID4, **kwargs) -> None:


class SummaryImage:
    crud = SummaryImageCRUD

    @classmethod
    async def create(cls, session: AsyncSession, summary_id, file_path) -> SummaryImageModel:
        return await cls.crud.create(session, path=file_path, summary_id=summary_id)

    @classmethod
    async def get(cls, session: AsyncSession, image_id) -> SummaryImageModel:
        return await cls.crud.get(session, "id", image_id)

    @classmethod
    async def delete(cls, session: AsyncSession, image_id) -> None:
        await cls.crud.delete(session, "id", image_id)