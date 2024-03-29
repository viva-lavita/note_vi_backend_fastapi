from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig
import time
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis

from src.auth.config import fastapi_users, current_active_user  # не убирать
from src.auth.router import router_auth, router_roles, router_users
from src.config import config, app_configs
from src.logs.config import LOG_CONFIG
from src.logs.middlewares import LoggingMiddleware
from src.tasks.router import router_tasks
from src.tasks.tasks import celery  # не убирать
from src.summary.router import router_summary


dictConfig(LOG_CONFIG)
logger = logging.getLogger('root')


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from src.auth.service import create_test_data, create_users
    await create_test_data()  # TODO: Убрать в проде
    await create_users()
    redis = aioredis.from_url(
        config.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.aclose()


app = FastAPI(
    **app_configs,
    lifespan=lifespan
)
app.middleware('http')(
    LoggingMiddleware()
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


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
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_roles)
app.include_router(router_tasks)
app.include_router(router_summary)
