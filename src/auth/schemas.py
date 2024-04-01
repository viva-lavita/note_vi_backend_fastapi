from datetime import datetime
from typing import Optional

from fastapi_users import schemas
from fastapi_users.jwt import JWT_ALGORITHM
from pydantic import UUID4, BaseModel, EmailStr, Field, validator
from sqlalchemy import TIMESTAMP

from src.auth.constants import Permission
from src.config import config


class RoleResponse(BaseModel):
    id: UUID4
    name: str
    permission: str

    class Config:
        from_attributes = True

    @validator("permission", pre=True, always=True)
    def set_permission(cls, v):
        return Permission[v]


class UserRead(schemas.BaseUser[UUID4]):
    """
    Схема для получения пользователя.
    Отсутствует поле с паролем.
    Есть поле с id.
    """
    id: UUID4
    email: EmailStr
    username: str
    role_id: UUID4
    registered_at: datetime
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    """
    Схема для создания пользователя.
    Отсутствует поле с id.
    """
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(min_length=5, max_length=64)
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False

    class Config:
        from_attributes = True
        json_schema_extra = {
            "required": ["username", "email", "password"],
            "example": {
                "username": "Viva",
                "email": "artyomsopin@yandex.ru",
                "password": "string"
            }
        }


class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема для обновления пользователя.
    Отсутствует поле с id.
    """
    username: str | None = Field(min_length=3, max_length=32, default=None)
    email: EmailStr | None = None
    password: str | None = Field(min_length=5, max_length=64, default=None)
    role_id: UUID4 | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class ShortUser(BaseModel):
    id: UUID4
    username: str

    class Config:
        from_attributes = True

class UserTokenVerifyRequest(BaseModel):

    class Config:
        from_attributes = True
