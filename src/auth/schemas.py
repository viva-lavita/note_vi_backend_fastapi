from typing import Optional

from fastapi_users import schemas
from fastapi_users.jwt import JWT_ALGORITHM
from pydantic import UUID4, BaseModel, EmailStr, validator

from src.auth.constants import Permission
from src.config import config


class RoleResponse(BaseModel):
    id: UUID4
    name: str
    permission: str


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
    # role: Optional[RoleResponse]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    """
    Схема для создания пользователя.
    Отсутствует поле с id.
    """
    username: str
    email: EmailStr
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False

    class Config:
        from_attributes = True


class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема для обновления пользователя.
    Отсутствует поле с id.
    """
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role_id: UUID4 | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None



class UserTokenVerifyRequest(BaseModel):

    class Config:
        from_attributes = True  # Можно не перечислять поля, если они не меняются
