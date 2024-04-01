from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import (TIMESTAMP, UUID, Boolean, ForeignKey,
                        String, text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import new_uuid
from src.database import Base
from src.models import CRUDBase, MixinID


# class TypeFile(str, Enum):
#     summary = "summary"
#     image = "image"
#     avatar = "avatar"
#     other = "other"


class File(Base):
    __tablename__ = "file"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str]
    path: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"))
    # type: Mapped[TypeFile] = mapped_column(default=TypeFile.other)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="files", lazy=False)

    def __str__(self):
        return f"File(name={self.name}, path={self.path})"

    def __repr__(self):
        return (
            f"File(id={self.id!r}, "
            f"name={self.name!r}, "
            f"path={self.path!r})"
        )


class FileCRUD(CRUDBase):
    table = File


class SummaryImage(Base):
    __tablename__ = "summary_image"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    path: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow)
    summary_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("summary.id", ondelete="CASCADE"))

    summary = relationship("Summary", back_populates="images", lazy=False)


class Summary(Base):
    __tablename__ = "summary"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(256), default='Not name')
    summary_path: Mapped[str]
    images: Mapped[list[SummaryImage] | None] = relationship(
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy=False
    )
    is_public: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"))

    author = relationship("User", back_populates="summaries", lazy=False)


class SummaryCRUD(CRUDBase):
    table = Summary
