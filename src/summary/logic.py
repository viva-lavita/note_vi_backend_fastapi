from uuid import UUID

from pydantic import UUID4
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.models import exactly_one, get_list
from src.summary.models import (
    SummaryCRUD, Summary as SummaryModel,
    SummaryImageCRUD, SummaryImage as SummaryImageModel, SummaryUserCRUD,
    SummaryUser as SummaryUserModel
)


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


class SummaryImage:
    crud = SummaryImageCRUD

    @classmethod
    async def create(
        cls, session: AsyncSession, summary_id, file_path
    ) -> SummaryImageModel:
        return await cls.crud.create(
            session, path=file_path, summary_id=summary_id)

    @classmethod
    async def get(cls, session: AsyncSession, image_id) -> SummaryImageModel:
        return await cls.crud.get(session, "id", image_id)

    @classmethod
    async def delete(cls, session: AsyncSession, image_id) -> None:
        await cls.crud.delete(session, "id", image_id)


class SummaryUser:
    crud = SummaryUserCRUD

    @classmethod
    async def create(
        cls, session: AsyncSession, summary_id: UUID, user_id: UUID
    ) -> SummaryUserModel | None:
        query = (select(SummaryUserModel)
                 .where((SummaryUserModel.user_id == user_id) &
                        (SummaryUserModel.summary_id == summary_id)))

        favorite_instance = (await session.execute(query)).first()
        if favorite_instance:
            return None
        return await cls.crud.create(
            session, summary_id=summary_id, user_id=user_id)

    @classmethod
    async def delete(
        cls, session: AsyncSession, summary_id: UUID, user_id: UUID
    ) -> None:
        query = delete(SummaryUserModel).where(
            (SummaryUserModel.user_id == user_id) &
            (SummaryUserModel.summary_id == summary_id)
        )
        await session.execute(query)
        await session.flush()

    @classmethod
    async def get(
        cls, session: AsyncSession, summary_id: UUID, user_id: UUID
    ) -> SummaryUserModel | None:
        query = select(SummaryUserModel).where(
            (SummaryUserModel.user_id == user_id) &
            (SummaryUserModel.summary_id == summary_id)
        )
        return await exactly_one(session, query)

    @classmethod
    async def get_list(
        cls, session: AsyncSession, user_id: UUID
    ) -> list[SummaryModel]:
        query = (select(SummaryModel)
                 .join(SummaryUserModel,
                       SummaryUserModel.summary_id == SummaryModel.id)
                 .where(SummaryUserModel.user_id == user_id)
        ).order_by(SummaryUserModel.created_at.desc())
        return await get_list(session, query)