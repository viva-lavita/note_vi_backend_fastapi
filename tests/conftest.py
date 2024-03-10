import asyncio
from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator, Tuple

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.testclient import TestClient
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from redis import asyncio as aioredis

from src.config import config
from src.tasks.tasks import celery
from src.database import (
    commit, custom_serializer, get_async_session, metadata, Base
)
from src.main import app
from src.models import get_by_name
from src.auth.models import Role, RoleCRUD


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

app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
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


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def redis() -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(
        config.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    yield redis
    await redis.aclose()


@pytest.fixture(autouse=True, scope="session")
def fastapi_cache(redis):
    FastAPICache.init(RedisBackend(redis), prefix="test-cache")


@pytest.fixture(scope="session", autouse=True)
async def roles():
    async with engine_test.begin() as conn:
        await conn.execute(Role.__table__.insert(),
                           [
                                {"name": "superuser", "permission": "superuser"},
                                {"name": "admin", "permission": "admin"},
                                {"name": "user", "permission": "user"},
                                {"name": "customer", "permission": "customer"}
                            ]
                           )


# @pytest.fixture
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()