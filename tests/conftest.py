import asyncio
from contextlib import asynccontextmanager
import datetime
import os
from typing import AsyncGenerator, List, Tuple
from passlib.context import CryptContext

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.testclient import TestClient
from fastapi_users.password import PasswordHelper
import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from redis import asyncio as aioredis

from src.auth.models import Permission, Role, RoleCRUD, User
from src.config import config
from src.database import (
    custom_serializer, get_async_session, metadata
)
from src.exceptions import new_uuid
from src.tasks.tasks import celery  # не убирать
from src.main import app



import contextlib

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


@pytest.fixture(scope="function")
async def role_user() -> Role:
    async with engine_test.begin() as conn:
        role = Role(id=new_uuid(), name="user", permission=Permission.user)
        await conn.execute(
            Role.__table__.insert().values(
                id=role.id,
                name=role.name,
                permission=role.permission
            )
        )
        return role


# @pytest.fixture(scope="function")
# async def auth_user(role_user) -> User:
#     """
#     Обычный аутентифицированный юзер.
#     """
#     async with engine_test.begin() as conn:
#         pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#         hashed_password = pwd_context.hash("auth_user_password")
#         user = User(
#             id=new_uuid(),
#             email="Wf9b6@example.com",
#             username="auth_user",
#             role_id=role_user.id,
#             hashed_password=hashed_password,
#             is_active=True,
#             is_superuser=False,
#             is_verified=True
#         )
#         await conn.execute(User.__table__.insert().values(
#             id=user.id,
#             email=user.email,
#             username=user.username,
#             role_id=user.role_id,
#             hashed_password=user.hashed_password,
#             is_active=user.is_active,
#             is_superuser=user.is_superuser,
#             is_verified=user.is_verified
#         ))
#         return user

get_async_session_context = contextlib.asynccontextmanager(override_get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
        email: str,
        password: str,
        username: str,
        is_superuser: bool = False
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
                        )
                    )
                    print(f"User created {user}")
                    return user
    except UserAlreadyExists:
        print(f"User {email} already exists")
        raise


@pytest.fixture(scope="function")
async def user(role_user) -> User:
    """
    Обычный аутентифицированный юзер.
    """
    return await create_user(
        email="Wf9b6@example.com",
        username="auth_user",
        password="auth_user_password",
    )


@pytest.fixture(scope="function")
async def auth_user(user) -> User:
    """
    Обычный аутентифицированный юзер.
    """
    async with async_session_maker() as session:
        async with session.begin():
            user.is_verified = True
            session.add(user)
            await session.commit()
    return user


@pytest.fixture(scope="function")
async def auth_headers(auth_user, ac: AsyncClient):
    """Заголовок аутентифицированного юзера."""
    data = {
        "username": auth_user.username,
        "password": "auth_user_password"
    }
    r = await ac.post("api/v1/auth/login", data=data)
    response = r.json()
    access_token = response["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    return headers

# Попробовать первый и второй варианты
class jwt_token:
    def __init__(self, auth_user):
        self.user = auth_user
        self.expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    def encode(self):
        """ Сгенерировать токен. """
        return jwt.encode(
            {
                "user_id": self.user.id,
                "exp": self.expiration
            },
            config.SECRET_AUTH_KEY,
            algorithm="HS256"
        )

    def decode(self):
        """ Декодировать токен. """
        return jwt.decode(
            self.encode(),
            config.SECRET_AUTH_KEY,
            algorithms=["HS256"]
        )

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.encode()}"
        }

    def get_query_params(self):
        return {
            "access_token": self.encode()
        }

    def get_token_cookie(self):
        return self.encode()

