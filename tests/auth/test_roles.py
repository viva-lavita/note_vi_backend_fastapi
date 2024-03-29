import logging
from httpx import AsyncClient

from fastapi import status
import pytest
from exceptions import ObjectNotFoundError

from src.auth.models import Role, User
from src.auth.logic import Role as RoleCRUD
from src.models import get_by_id, get_by_name
from tests.conftest import (
    engine_test,  # не удалять engine_test, первый и последний тесты упадут
    async_session_maker,
    get_async_session_context
)


logger = logging.getLogger('tests')


class TestRoles:
    url = "api/v1/roles/"

    async def test_get_roles_list(
            self, ac: AsyncClient, auth_verif_user: tuple[User, dict]
    ) -> None:
        """Получение списка ролей current_active_verified_user."""
        _, auth_headers = auth_verif_user
        response = await ac.get(self.url, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4

    async def test_get_role_by_id(
            self, ac: AsyncClient, auth_verif_user: tuple[User, dict]
    ):
        """Получение роли по id."""
        user, auth_headers = auth_verif_user
        async with get_async_session_context() as session:
            role = await get_by_id(session, Role, user.role_id)
            assert role
            response = await ac.get(
                f"{self.url}{role.id}", headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["name"] == role.name

    async def test_delete_role(
            self, ac: AsyncClient, auth_superuser: tuple[User, dict]
    ):
        """Удаление роли по id."""
        _, headers = auth_superuser
        async with get_async_session_context() as session:
            role = await get_by_name(session, Role, 'customer')
            assert role.name == 'customer'
            response = await ac.delete(
                f"{self.url}{role.id}", headers=headers
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT
            role = await get_by_name(session, Role, 'customer')
            assert role is None
