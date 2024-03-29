from datetime import datetime

from sqlalchemy import (TIMESTAMP, UUID, Boolean, ForeignKey,
                        String)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import new_uuid
from src.database import Base
from src.models import CRUDBase, MixinID


class File(Base):
    __tablename__ = "file"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                 default=datetime.utcnow)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"),
                                          nullable=False)

    user = relationship("User", back_populates="files")

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
