from typing import Union

from fastapi import FastAPI

from src.config import config, app_configs
from src.auth.config import fastapi_users  # не убирать
from src.auth.router import router_auth, router_roles, router_users


app = FastAPI(
    **app_configs
)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_roles)
