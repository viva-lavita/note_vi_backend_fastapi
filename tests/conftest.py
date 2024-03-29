import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import status
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from redis import asyncio as aioredis

from src.auth.models import Permission, Role, User
from src.config import config
from src.database import (
    custom_serializer, get_async_session, metadata
)
from src.constants import new_uuid
from src.tasks.tasks import celery  # не убирать
from src.main import app


from fastapi_users.exceptions import UserAlreadyExists

from src.auth.schemas import UserCreate
from src.auth.manager import get_user_manager
from src.auth.utils import get_user_db


engine_test = create_async_engine(
    config.POSTGRES_URI_TEST,
    echo=config.POSTGRES_ECHO_TEST,
    future=True,
    isolation_level="READ COMMITTED",  # Не изменять
    json_serializer=custom_serializer,
    pool_pre_ping=True,
    pool_timeout=1,
    pool_size=10
)
async_session_maker = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True
)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True, scope='function')
async def prepare_database():
    async with engine_test.begin() as conn:
        app.dependency_overrides[get_async_session] = override_get_async_session
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    yield
    app.dependency_overrides[get_async_session] = get_async_session
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
async def redis() -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(
        config.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    yield redis
    await redis.aclose()


@pytest.fixture(autouse=True, scope="function")
def fastapi_cache(redis):
    FastAPICache.init(RedisBackend(redis), prefix="test-cache")


get_async_session_context = asynccontextmanager(override_get_async_session)
get_user_db_context = asynccontextmanager(get_user_db)
get_user_manager_context = asynccontextmanager(get_user_manager)


async def create_user(
        email: str,
        password: str,
        username: str,
        is_superuser: bool = False,
        is_verified: bool = False
):
    """Создание юзера программно для тестов."""
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            email=email,
                            username=username,
                            password=password,
                            is_superuser=is_superuser,
                            is_verified=is_verified
                        )
                    )
                    print(f"User created {user}")
                    return user
    except UserAlreadyExists:
        print(f"User {email} already exists")
        raise


@pytest.fixture(scope="function")
async def roles():
    async with engine_test.begin() as conn:
        roles_data = [
            {"id": new_uuid(), "name": "superuser", "permission": Permission.superuser},
            {"id": new_uuid(), "name": "admin", "permission": Permission.admin},
            {"id": new_uuid(), "name": "user", "permission": Permission.user},
            {"id": new_uuid(), "name": "customer", "permission": Permission.customer}
        ]
        roles = [Role(**role) for role in roles_data]
        for role in roles:
            await conn.execute(Role.__table__.insert().values(
                id=role.id,
                name=role.name,
                permission=role.permission
            ))
        return roles


# @pytest.fixture(scope="function")
# async def role_user() -> Role:
#     async with engine_test.begin() as conn:
#         role = Role(id=new_uuid(), name="user", permission=Permission.user)
#         await conn.execute(
#             Role.__table__.insert().values(
#                 id=role.id,
#                 name=role.name,
#                 permission=role.permission
#             )
#         )
#         return role


@pytest.fixture(scope="function")
async def user(roles) -> User:
    """
    Обычный зарегистрированный юзер.
    """
    return await create_user(
        email="user@example.com",
        username="user",
        password="user_password",
    )


@pytest.fixture(scope="function")
async def verif_user(roles) -> User:
    """
    Верифицированный юзер.
    """
    return await create_user(
        email="user2@example.com",
        username="user",
        password="user_password",
        is_verified=True
    )


@pytest.fixture(scope="function")
async def superuser(roles) -> User:
    """
    Суперюзер.
    """
    return await create_user(
        email="superuser@example.com",
        username="superuser",
        password="superuser_password",
        is_superuser=True,
        is_verified=True
    )


async def get_auth_headers(ac, data):
    response = await ac.post("api/v1/auth/login", data=data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    access_token = response.cookies.get("Bearer")
    headers = {
        "Cookie": f"Bearer={access_token}"
    }
    return headers


@pytest.fixture(scope="function")
async def auth_user(ac, user) -> User:
    """Авторизованный в системе не верифицированный юзер."""
    data = {
        "username": user.email,
        "password": "user2_password"
    }
    headers = await get_auth_headers(ac, data)
    return user, headers


@pytest.fixture(scope="function")
async def auth_verif_user(ac, verif_user) -> User:
    """Авторизованный в системе верифицированный юзер."""
    # async with get_async_session_context() as session:
    #     async with session.begin():
    #         user.is_verified = True
    #         session.add(user)
    #         await session.commit()

    data = {
        "username": verif_user.email,
        "password": "user_password"
    }
    headers = await get_auth_headers(ac, data)
    return verif_user, headers


@pytest.fixture(scope="function")
async def auth_superuser(ac, superuser) -> tuple[User, dict]:
    """Авторизованный в системе суперюзер."""
    data = {
        "username": superuser.email,
        "password": "superuser_password"
    }
    headers = await get_auth_headers(ac, data)
    return superuser, headers

# @pytest.fixture(scope="function")
# async def auth_headers(auth_user, ac: AsyncClient):
#     """Заголовок аутентифицированного юзера."""
#     data = {
#         "username": auth_user.email,
#         "password": "auth_user_password"
#     }
#     response = await ac.post("api/v1/auth/login", data=data)
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     access_token = response.cookies.get("Bearer")
#     headers = {
#         "Cookie": f"Bearer={access_token}"
#     }
#     return headers
