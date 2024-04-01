from typing import Any, Optional, Type, TypeVar

from sqlalchemy import UUID, delete, func, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select

from src.constants import new_uuid
from src.database import Base
from src.exceptions import ObjectNotFoundError

Table = TypeVar("Table", bound=Base)


class MixinID:
    """Миксин добавления id в таблицы."""
    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=new_uuid)


class CRUDBase:
    table: Type[Table]

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> Table:
        created_fields = {k: v for k, v in kwargs.items()
                          if getattr(cls.table, k, None) is not None}
        instance = cls.table(**created_fields)
        session.add(instance)
        await session.flush()
        return instance

    @classmethod
    async def get(cls, session: AsyncSession, field: str, value: Any) -> Table:
        query = select(cls.table).where(getattr(cls.table, field) == value)
        return await exactly_one(session, query)

    @classmethod
    async def update(
        cls, session: AsyncSession, field: str, value: Any, **kwargs
    ) -> None:
        updated_fields = {k: v for k, v in kwargs.items()
                          if getattr(cls.table, k, None) is not None}
        query = update(cls.table).where(
            getattr(cls.table, field) == value
        ).values(**updated_fields)
        await session.execute(query)
        await session.flush()

    @classmethod
    async def delete(
        cls, session: AsyncSession, field: str, value: Any
    ) -> None:
        query = delete(cls.table).where(getattr(cls.table, field) == value)
        await session.execute(query)
        await session.flush()


async def get_list(session: AsyncSession, query: Select) -> list[Table]:
    """
    Метод позволяет получить список объектов.
    На вход подаются следующие параметры:
    session - сессия
    query - запрос в формате sqlalchemy, например:
    select(User).where(User.name == 'John')
    """
    return (await session.execute(query)).unique().scalars().all()


async def exactly_one(session: AsyncSession, query) -> Optional[Table]:
    """
    Получает одно скалярное значение из результата запроса.

    Параметры:
    session - сессия
    query - запрос в формате SQLAlchemy, например:
    session.query(User).filter(User.name == 'John')
    Вернет пользователя с именем John

    Возвращает:
    Элемент, соответствующий запросу

    Исключения:
    ObjectNotFoundError - если результат запроса пуст
    MultipleResultFound - если результат запроса содержит более одного элемента
    """
    try:
        return (await session.execute(query)).unique().scalars().one()
    except NoResultFound:
        raise ObjectNotFoundError


async def get_total_rows(session: AsyncSession, query: Select) -> int:
    """
    Метод позволяет получить общее количество элементов.

    :param session: сессия
    :param query: запрос в формате SQLAlchemy, например:
    select(User).where(User.name == 'John')

    :return: Общее количество элементов, соответствующих запросу.

    Исключения:
    ObjectNotFoundError - если результат запроса пуст
    MultipleResultFound - если результат запроса содержит более одного элемента
    """
    return (
        await session.execute(select(func.count())
                              .select_from(query.subquery()))
            ).scalars().one()


async def get_by_name(
        session: AsyncSession, table: Type[Table], name: str
) -> Optional[Table]:
    """
    Возвращает объект по полю 'name'.

    :param session: асинхронная сессия
    :param table: класс sqlalchemy (из файлов models.py)
    :param name: значение поля 'name'
    :return: экземпляр класса
    """
    return (
        await session.execute(select(table).where(table.name == name))
    ).unique().scalars().first()


async def get_by_id(
        session: AsyncSession, table: Type[Table], id: str
) -> Optional[Table]:
    query = select(table).where(table.id == id)
    return await exactly_one(session, query)
