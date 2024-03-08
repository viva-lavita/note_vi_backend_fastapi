from contextlib import asynccontextmanager
from typing import AsyncGenerator, Union

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis

from src.config import config, app_configs
from src.auth.config import fastapi_users  # не убирать
from src.tasks.tasks import celery
from src.auth.router import router_auth, router_roles, router_users
from src.tasks.router import router_tasks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from src.auth.service import create_roles
    await create_roles()  # Убрать в проде
    redis = aioredis.from_url(
        config.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()


app = FastAPI(
    **app_configs,
    lifespan=lifespan
)

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://127.0.0.1",
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie",
                   "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_roles)
app.include_router(router_tasks)


# @app.on_event("startup")
# async def startup_event():
#     redis = aioredis.from_url(
#         config.REDIS_URL,
#         encoding="utf8",
#         decode_responses=True
#     )
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
