from httpx import AsyncClient
from fastapi import status

from src.exceptions import ObjectNotFoundError
from src.auth.logic import UserTokenVerify
from src.auth.models import Role, User
from src.config import config
from tests.conftest import (
    engine_test,  # не удалять engine_test, первый и последний тесты упадут
    async_session_maker, get_async_session_context
)


class TestRegister:
    api_version = "api/v1"
    url_register = f"{api_version}/auth/register"
    url_request_verify = f"{api_version}/auth/request-verify-token"
    url_accept = f"{api_version}/auth/accept"
    url_login = f"{api_version}/auth/login"
    url_users = f"{api_version}/users"

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

    async def test_verivication_user(
            self, ac: AsyncClient, user: User
    ) -> None:
        """Тестирование верификации пользователя."""

        assert user.is_verified is False
        # Отправляем несколько запросов, чтобы проверить, что токены заменяются
        response = await ac.post(
            self.url_request_verify,
            json={
                "email": user.email
            }
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        response = await ac.post(
            self.url_request_verify,
            json={
                "email": user.email
            }
        )
        assert response.status_code == status.HTTP_202_ACCEPTED

        # Получаем токен
        async with get_async_session_context() as session:
            token = await UserTokenVerify.crud.get(session, 'user_id', user.id)
            assert token

            # Верифицируемся
            response = await ac.get(
                f'{self.url_accept}?token={token.token_verify}',
            )
            assert response.status_code == status.HTTP_200_OK

            user = await session.get(User, user.id)
            assert user.is_verified is True
            assert user.is_active is True
            assert user.is_superuser is False

            # Проверяем, что временный токен удалился и больше токенов нет.
            try:
                await UserTokenVerify.crud.get(session, 'user_id', user.id)
                assert False
            except ObjectNotFoundError:
                pass
            except Exception:
                assert False

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
