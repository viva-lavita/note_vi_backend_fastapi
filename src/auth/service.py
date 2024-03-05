import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import get_by_name
from src.auth.models import Role, RoleCRUD
from src.database import commit, async_session


async def create_roles() -> None:
    async with async_session() as session:
        try:
            async with commit(session) as session:
                if await get_by_name(session, Role, "superuser"):
                    print("Roles already created")
                    return
                await RoleCRUD().create(
                    session=session, name="superuser", permission="superuser"
                )
                await RoleCRUD().create(
                    session=session, name="admin", permission="admin"
                )
                await RoleCRUD().create(
                    session=session, name="user", permission="user"
                )
                await RoleCRUD().create(
                    session=session, name="customer", permission="customer"
                )
                print("Roles created")
        except Exception as e:
            print(e)  # TODO: Добавить логирование


if __name__ == "__main__":
    try:
        asyncio.run(create_roles())
    except Exception as e:
        print(e)
