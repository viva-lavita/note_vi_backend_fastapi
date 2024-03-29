import asyncio
from contextlib import asynccontextmanager
from select import select
from fastapi_users.exceptions import UserAlreadyExists

from src.auth.manager import get_user_manager
from src.auth.schemas import UserCreate
from src.auth.utils import get_user_db
from src.exceptions import ObjectNotFoundError
from src.auth.models import Role, UserCRUD
from src.auth.logic import Role as RoleCRUD
from src.database import commit, async_session, get_async_session
from src.models import get_by_name


get_async_session_context = asynccontextmanager(get_async_session)
get_user_db_context = asynccontextmanager(get_user_db)
get_user_manager_context = asynccontextmanager(get_user_manager)


async def create_user(
        email: str,
        password: str,
        username: str,
        is_superuser: bool = False,
        is_verified: bool = False
):
    """Создание юзера программно для разработки."""
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


async def create_test_data() -> None:
    async with async_session() as session:
        try:
            async with commit(session) as session:
                if await get_by_name(session, Role, "superuser"):
                    print("Roles already created")
                    return
                await RoleCRUD.get_or_create(
                    session=session, name="superuser", permission="superuser"
                )
                await RoleCRUD.get_or_create(
                    session=session, name="admin", permission="admin"
                )
                await RoleCRUD.get_or_create(
                    session=session, name="user", permission="user"
                )
                await RoleCRUD.get_or_create(
                    session=session, name="customer", permission="customer"
                )
                print("Roles created")
        except Exception as e:
            print(e)  # TODO: Добавить логирование


async def create_users() -> None:
    async with async_session() as session:
        try:
            async with commit(session) as session:
                try:
                    await UserCRUD.get(session, "email", "admin@example.com")
                    print("User admin already created")
                except ObjectNotFoundError:
                    await create_user(email="admin@example.com",  # добавила админа
                                      password="admin",
                                      username="admin",
                                      is_superuser=True,
                                      is_verified=True)
                    print("User admin created")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    try:
        asyncio.run(create_test_data())
    except Exception as e:
        print(e)
