from httpx import AsyncClient, HTTPStatusError
from fastapi import status

from src.auth.models import Role, User
from src.config import config
from tests.conftest import (
    engine_test,  # не удалять engine_test, первый и последний тесты упадут
    async_session_maker, get_async_session_context
)


class TestRegister:
    url_register = "api/v1/auth/register"
    url_login = "api/v1/auth/login"
    url_users = "api/v1/users"

    async def test_register(self, ac: AsyncClient, roles: list[Role]) -> None:
        """
        Регистрация нового пользователя.

        Тестирование возможности регистрации нового пользователя, а
        так проверка, что пользователь не может присвоить себе роль.
        """
        response = await ac.post(
            self.url_register,
            json={
                "email": config.SMTP_USER,
                "password": "string",
                "username": "string1",
                "role_id": roles[1].id
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == config.SMTP_USER
        assert response.json()["username"] == "string1"
        assert response.json()["role_id"] == roles[2].id
        async with get_async_session_context() as session:
            user = await session.get(User, response.json()["id"])
            assert user

    async def test_register_already_exists(
            self, ac: AsyncClient, user: User
    ) -> None:
        """Повторная регистрация уже существующего пользователя."""
        response = await ac.post(
            self.url_register,
            json={
                "email": user.email,
                "password": "user_password",
                "username": user.username
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "REGISTER_USER_ALREADY_EXISTS"
        }

    async def test_login_auth_user(
            self, ac: AsyncClient, verif_user: tuple[User, dict]
    ):
        """Авторизация пользователя."""
        auth_user, _ = verif_user
        response = await ac.post(
            self.url_login,
            data={
                "username": auth_user.email,
                "password": "user_password"
            }
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_get_me_auth_user(
            self, ac: AsyncClient, verif_user: tuple[User, dict]
    ):
        """Получение информации о пользователе."""
        auth_user, auth_headers = verif_user
        response = await ac.get(
            self.url_users + "/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == auth_user.email
        assert data["username"] == auth_user.username
        assert data["role_id"] == str(auth_user.role_id)
