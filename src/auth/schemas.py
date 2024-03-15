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



class UserTokenVerifyRequest(BaseModel):

    # @validator('token_verify')
    # def check_jwt_token(cls, v):
    #     try:
    #         token = jwt.decode(v, config.SECRET_AUTH_KEY, algorithms=JWT_ALGORITHM)
    #         # Уточнить срок времени жизни токена и дописать проверку
    #     except jwt.ExpiredSignatureError:
    #         raise ValueError('Token has expired')
    #     except jwt.InvalidTokenError:
    #         raise ValueError('Invalid token')
    #     return v

    class Config:
        from_attributes = True  # Можно не перечислять поля, если они не меняются
