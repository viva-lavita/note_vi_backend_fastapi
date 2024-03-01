from typing import Optional

from fastapi import Depends, Request
from fastapi_users import (BaseUserManager, IntegerIDMixin, exceptions, models,
                           schemas)

from auth.models import User
from auth.utils import get_user_db
from src.config import config


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):  # TODO: рассмотреть замену на UUIDIDMixin
    """
    Менеджер пользователей.
    Реализует взаимодействие с пользователями.

    Переопределили метод create, чтобы присвоить роль по умолчанию.
    """
    reset_password_token_secret = config.SECRET_AUTH
    verification_token_secret = config.SECRET_AUTH

    async def on_after_register(
            self, user: User, request: Optional[Request] = None
    ):
        """
        Действия после регистрации пользователя.
        Тут можно дописать отправку письма с подтверждением регистрации.
        """
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Действия после восстановления пароля.
        Тут можно дописать отправку письма с подтверждением
        восстановления пароля.
        """
        print(f"User {user.id} has forgot their password. "
              f"Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Действия после запроса верификации пользователя.
        """
        print(f"Verification requested for user {user.id}. "
              f"Verification token: {token}")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_name"] = config.ROLE_DEFAULT  # TODO: Пересмотреть роль по умолчанию

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
