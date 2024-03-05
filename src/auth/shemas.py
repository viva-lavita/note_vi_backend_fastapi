from typing import Optional

from fastapi_users import schemas
from pydantic import UUID4, BaseModel, EmailStr


class UserRead(schemas.BaseUser[int]):
    """
    Схема для получения пользователя.
    Отсутствует поле с паролем.
    Есть поле с id.
    """
    id: UUID4
    email: EmailStr
    username: str
    role_id: UUID4
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
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    class Config:
        from_attributes = True


class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема для обновления пользователя.
    Отсутствует поле с id.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class RoleResponse(BaseModel):
    id: UUID4
    name: str
    permission: str
