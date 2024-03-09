from typing import AsyncGenerator
from httpx import AsyncClient

from fastapi.testclient import TestClient
import pytest

from src.constants import Environment
from src.main import app


@pytest.fixture(scope="module")
def client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# def test_create_user(mocker): # Нужен установленый pytest-mock
#     # создание мокированного подключения к базе данных
#     mock_db = mocker.MagicMock(Database)
#     app.dependency_overrides[Database] = mock_db

#     # выполнение тестового запроса к вашему приложению
#     with TestClient(app) as client:
#         response = client.post("/users/", json={"username": "testuser"})
#         assert response.status_code == 200
#         assert response.json() == {"username": "testuser"}

#     # проверка вызовов к мокированной базе данных
#     mock_db.create_user.assert_called_once_with("testuser")