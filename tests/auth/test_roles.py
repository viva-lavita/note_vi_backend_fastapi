from httpx import AsyncClient

from fastapi import status
import pytest

from src.auth.models import Role, User
from src.models import get_by_id, get_by_name
from tests.conftest import (
    engine_test,  # не удалять engine_test, первый и последний тесты упадут
    async_session_maker,
    get_async_session_context
)


class TestRoles:
    url = "api/v1/roles/"

    async def test_get_roles_list(
            self, ac: AsyncClient, verif_user: tuple[User, dict]
    ) -> None:
        """Получение списка ролей current_active_verified_user."""
        _, auth_headers = verif_user
        response = await ac.get(self.url, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4

    async def test_get_role_by_id(
            self, ac: AsyncClient, verif_user: tuple[User, dict]
    ):
        """Получение роли по id."""
        user, auth_headers = verif_user
        async with get_async_session_context() as session:
            role = await get_by_id(session, Role, user.role_id)
            assert role
            response = await ac.get(
                f"{self.url}{role.id}", headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["name"] == role.name
