from datetime import datetime
import uuid

from sqlalchemy import (TIMESTAMP, UUID, Boolean, Column, ForeignKey,
                        String, Table, text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import new_uuid
from src.database import Base, metadata
from src.models import CRUDBase


# user_notes = Table(
#     "favorite_notes",
#     metadata,
#     Column("user_id", UUID, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
#     Column("note_id", UUID, ForeignKey("note.id", ondelete="CASCADE"), primary_key=True)
# )


class NoteUser(Base):
    __tablename__ = "note_user"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    note_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("note.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    note = relationship("Note", back_populates="favorite_users", lazy=False)
    user = relationship("User", back_populates="favorite_notes", lazy=False)


class ImageNote(Base):
    __tablename__ = "image_note"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    path: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    note_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("note.id",
                                                          ondelete="CASCADE"))

    note = relationship("Note", back_populates="images", lazy=False)


class ImageNoteCRUD(CRUDBase):
    table = ImageNote


class Note(Base):
    __tablename__ = "note"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(256))
    intro: Mapped[str] = mapped_column(String(512))
    text: Mapped[str]
    is_public: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow,
                                                 onupdate=datetime.utcnow)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id",
                                                            ondelete="CASCADE"))

    author = relationship("User", back_populates="notes", lazy=False)
    favorite_users= relationship(
        "NoteUser",
        back_populates="note",
    )
    images: Mapped[list[ImageNote] | None] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"Note(id={self.id!r}, author_id={self.author_id!r})"

    def __str__(self):
        return f"Note id={self.id}, author_id={self.author_id}"


class NoteCRUD(CRUDBase):
    table = Note
