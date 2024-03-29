from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import (TIMESTAMP, UUID, Boolean, ForeignKey,
                        String)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.constants import Permission
from src.database import Base
from src.models import CRUDBase, MixinID


class Role(Base, MixinID):
    __tablename__ = "role"

    name: Mapped[str] = mapped_column(String,
                                      nullable=False,
                                      unique=True)
    permission: Mapped[Permission] = mapped_column(ENUM(Permission),
                                                   nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __str__(self):
        return (
            f"Person(name={self.name}, "
            f"age={self.age}), "
            f"permission={self.permission}"
        )

    def __repr__(self):
        return (
            f"Role(id={self.id!r}, "
            f"name={self.name!r}, "
            f"permission={self.permission!r})"
        )


class User(SQLAlchemyBaseUserTableUUID, Base, MixinID):
    """
    Модель пользователя.
    Если is_active = False, то запросы на вход в систему и
    "забыли пароль" будут отклонены.
    """
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String,
                                       nullable=False,
                                       unique=True)
    username: Mapped[str] = mapped_column(String,
                                          nullable=False,
                                          unique=True)
    registered_at = mapped_column(TIMESTAMP,
                                  default=datetime.utcnow)
    updated_at = mapped_column(TIMESTAMP,
                               default=datetime.utcnow,
                               onupdate=datetime.utcnow)
    role_id: Mapped[UUID] = mapped_column(UUID,
                                          ForeignKey("role.id",
                                                     ondelete="RESTRICT"),
                                          nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024),
                                                 nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,
                                            default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean,
                                               default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean,
                                              default=False)

    role: Mapped["Role"] = relationship(back_populates="users")

    def __str__(self):
        return f"Person(username={self.username}, email={self.email})"

    def __repr__(self):
        return (
            f"User(id={self.id!r}, "
            f"username={self.username!r}, "
            f"email={self.email!r})"
        )


class UserTokenVerify(Base, MixinID):
    __tablename__ = "user_tokens"

    user_id: Mapped[UUID] = mapped_column(UUID,
                                          ForeignKey("user.id",
                                                     ondelete="CASCADE"),
                                          nullable=False)
    token_verify: Mapped[str] = mapped_column(String,
                                              nullable=False)

    def __str__(self):
        return (
            f"Person(user_id={self.user_id}, "
            f"token_verify={self.token_verify})"
        )

    def __repr__(self):
        return (
            f"UserTokenVerify(id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"token_verify={self.token_verify!r})"
        )


class RoleCRUD(CRUDBase):
    table = Role


class UserTokenVerifyCRUD(CRUDBase):
    table = UserTokenVerify
