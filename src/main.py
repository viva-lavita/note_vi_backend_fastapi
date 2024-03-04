from typing import Union

from fastapi import FastAPI

from src.config import config, app_configs
from src.auth.shemas import UserRead
from src.auth.config import fastapi_users
from src.auth.router import router_auth, router_users


app = FastAPI(
    **app_configs
)

app.include_router(router_auth)
app.include_router(router_users)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/users/{user_id}")
def update_item(user_id: str, user: UserRead):
    return {"user_name": user.name, "user_id": user_id}
