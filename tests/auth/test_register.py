from httpx import AsyncClient, HTTPStatusError
from fastapi import status

from tests.conftest import engine_test


class TestRegister:
    url_register = "api/v1/auth/register"

    async def test_register(self, ac: AsyncClient) -> None:
        """Регистрация нового пользователя."""
        response = await ac.post(
            self.url_register,
            json={
                "email": "artyomsopin@yandex.ru",
                "password": "string",
                "username": "string1"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == "artyomsopin@yandex.ru"

    async def test_register_already_exists(self, ac: AsyncClient) -> None:
        """Регистрация уже существующего пользователя."""
        response = await ac.post(
            self.url_register,
            json={
                "email": "artyomsopin@yandex.ru",
                "password": "string",
                "username": "string1"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "REGISTER_USER_ALREADY_EXISTS"
        }
