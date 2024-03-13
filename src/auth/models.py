from datetime import datetime
from fastapi import Depends

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import (JSON, TIMESTAMP, UUID, Boolean, Column, ForeignKey,
                        String, Table)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.auth.constants import Permission
from src.database import Base
from src.exceptions import new_uuid
from src.models import CRUDBase


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID, primary_key=True, default=new_uuid)
    name = Column(String, nullable=False, unique=True)
    permission = Column(ENUM(Permission), nullable=False)

# class Model(DeclarativeBase):
#     pass


# class Role(Model):
#     __tablename__ = "role"
#     id: Mapped[UUID] = mapped_column(primary_key=True, default=new_uuid)
#     name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
#     permission: Mapped[Permission] = mapped_column(ENUM(Permission), nullable=False)


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    Модель пользователя.
    Если is_active = False, то запросы на вход в систему и
    "забыли пароль" будут отклонены.
    """
    __tablename__ = "user"

    id = Column(UUID, primary_key=True, default=new_uuid)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(UUID, ForeignKey("role.id"), nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)

    role = relationship("Role", backref=backref("users", uselist=True))
    # back_populates


class UserTokenVerify(Base):
    __tablename__ = "user_tokens"

    id = Column(UUID, primary_key=True, default=new_uuid)
    user_id = Column(UUID,
                     ForeignKey("user.id", ondelete="CASCADE"),
                     nullable=False)
    token_verify = Column(String)


class RoleCRUD(CRUDBase):
    table = Role


class UserTokenVerifyCRUD(CRUDBase):
    table = UserTokenVerify


# async def get_user_db(session: AsyncSession = Depends(get_async_session)):
#     yield SQLAlchemyUserDatabase(session, User)

# from typing import Union

# from pydantic import BaseModel
# from sqlalchemy import Column, DateTime, String
# from sqlalchemy.dialects.postgresql import ENUM

# from src.database import Base
# from src.exceptions import new_uuid
# from src.models import CRUDBase


# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True)
#     name = Column(String)
#     email = Column(String)
#     password = Column(String)
#     created_at = Column(DateTime(), nullable=False)
#     updated_at = Column(DateTime)


# class Account(Base):
#     __tablename__ = "accounts"

#     id = Column(String(36), primary_key=True, default=new_uuid)
#     permission = Column(ENUM(Permission), nullable=False)
#     created_at = Column(DateTime(), nullable=False)


# class AccountCRUD(CRUDBase):
#     table = Account
