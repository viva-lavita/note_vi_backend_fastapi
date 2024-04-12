from datetime import datetime
import uuid

from sqlalchemy import (TIMESTAMP, UUID, Boolean, Column, ForeignKey,
                        String, Table, text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import new_uuid
from src.database import Base, metadata
from src.models import CRUDBase, MixinID


# summary_users = Table(
#     "summary_users",
#     metadata,
#     Column("user_id", UUID, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
#     Column("summary_id", UUID, ForeignKey("summary.id", ondelete="CASCADE"), primary_key=True)
# )

class SummaryUser(Base):
    __tablename__ = "summary_user"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    summary_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("summary.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    summary = relationship(
        "Summary", back_populates="favorite_users", lazy=False)
    user = relationship(
        "User", back_populates="favorite_summaries", lazy=False)


class SummaryUserCRUD(CRUDBase):
    table = SummaryUser


class SummaryImage(Base):
    __tablename__ = "summary_image"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    path: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow)
    summary_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("summary.id", ondelete="CASCADE"))

    summary = relationship("Summary", back_populates="images", lazy=False)

    def __str__(self):
        return f"SummaryImage(path={self.path})"

    def __repr__(self):
        return (
            f"SummaryImage(id={self.id!r}, "
            f"path={self.path!r})"
        )


class SummaryImageCRUD(CRUDBase):
    table = SummaryImage


class Summary(Base):
    __tablename__ = "summary"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(256), default='Not name')
    summary_path: Mapped[str] = mapped_column(String, unique=True)
    images: Mapped[list[SummaryImage] | None] = relationship(
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy=False
    )
    is_public: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id",
                                                            ondelete="CASCADE"))

    author = relationship("User", back_populates="summaries", lazy=False)
    favorite_users = relationship(
        "SummaryUser",
        back_populates="summary"
    )


class SummaryCRUD(CRUDBase):
    table = Summary
