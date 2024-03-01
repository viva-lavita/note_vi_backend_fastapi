from typing import Union

from fastapi import FastAPI
# from pydantic import BaseModel

from src.auth.shemas import UserRead

app = FastAPI(
    title="Note_vi_backend",
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/users/{user_id}")
def update_item(user_id: str, user: UserRead):
    return {"user_name": user.name, "user_id": user_id}
