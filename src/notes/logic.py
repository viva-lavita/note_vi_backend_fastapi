from uuid import UUID

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.notes.models import (
    ImageNote as ImageNoteModel, ImageNoteCRUD, NoteCRUD, Note as NoteModel
)

from src.auth.models import User
from src.models import get_list


class Note:
    crud = NoteCRUD

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> NoteModel:
        created_fields = dict(**kwargs)
        return await cls.crud.create(session, **created_fields)

    @classmethod
    async def get(cls, session: AsyncSession, note_id: UUID4) -> NoteModel:
        return await cls.crud.get(session, "id", note_id)

    @classmethod
    async def get_list(
        cls, session: AsyncSession, user_id: UUID | None = None,
        is_public: bool | None = None, username: str | None = None
    ) -> list[NoteModel]:
        query = select(NoteModel).order_by(NoteModel.created_at.desc())
        if user_id:
            query = query.filter(NoteModel.author_id == user_id)
        if is_public is not None:
            query = query.filter(NoteModel.is_public == is_public)
        if username:
            query = query.join(User).filter(User.username == username)
        return await get_list(session, query)

    @classmethod
    async def delete(cls, session: AsyncSession, note_id: UUID4) -> None:
        await cls.crud.delete(session, "id", note_id)

    @classmethod
    async def update(
        cls, session: AsyncSession, note_id: UUID4, new_note
    ) -> None:
        updated_fields = new_note.model_dump(exclude_unset=True)
        return await cls.crud.update(
            session, "id", note_id, **updated_fields)


class ImageNote:
    crud = ImageNoteCRUD

    @classmethod
    async def create(cls, session: AsyncSession, note_id, file_path) -> ImageNoteModel:
        return await cls.crud.create(session, path=file_path, note_id=note_id)

    @classmethod
    async def delete(cls, session: AsyncSession, image_id: UUID4) -> None:
        await cls.crud.delete(session, "id", image_id)

    @classmethod
    async def get(cls, session: AsyncSession, image_id: UUID4) -> ImageNoteModel:
        return await cls.crud.get(session, "id", image_id)
