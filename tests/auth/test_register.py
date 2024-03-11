from httpx import AsyncClient, HTTPStatusError
from fastapi import status
from src.models import get_by_name

from src.auth.models import Role, User
from tests.conftest import engine_test, async_session_maker, jwt_token # не удалять, первый и последний тесты упадут


class TestRegister:
    url_register = "api/v1/auth/register"
    url_login = "api/v1/auth/login"

    async def test_register(self, ac: AsyncClient, roles: list[Role]) -> None:
        """Регистрация нового пользователя."""
        response = await ac.post(
            self.url_register,
            json={
                "email": "artyomsopin@yandex.ru",
                "password": "string",
                "username": "string1",
                "role_id": roles[1].id
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == "artyomsopin@yandex.ru"
        assert response.json()["username"] == "string1"
        assert response.json()["role_id"] == roles[2].id

    async def test_register_already_exists(
            self, ac: AsyncClient, user: User
    ) -> None:
        """Регистрация уже существующего пользователя."""
        response = await ac.post(
            self.url_register,
            json={
                "email": user.email,
                "password": "string",
                "username": user.username
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "REGISTER_USER_ALREADY_EXISTS"
        }

    async def test_login_auth_user(self, ac: AsyncClient, auth_user: User):
        """Авторизация пользователя."""
        response = await ac.post(
            self.url_login,
            data={
                "username": auth_user.email,
                "password": "auth_user_password"
            }
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_get_roles_list(
            self, ac: AsyncClient, roles: list[Role]
    ) -> None:
        """Получение списка ролей."""
        response = await ac.get("api/v1/roles/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4

    async def test_get_role_by_id(
            self, ac: AsyncClient, roles: list[Role]
    ):
        """Получение роли по id."""
        async with async_session_maker() as session:
            role = await get_by_name(session, Role, roles[0].name)
            response = await ac.get(f"api/v1/roles/{role.id}")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["name"] == role.name
