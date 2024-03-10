from contextlib import asynccontextmanager
from datetime import date
from datetime import datetime
import enum
from functools import partial
from functools import wraps
import json
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import config
# from src.auth.models import User


class DatetimeAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, enum.Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)


custom_serializer = partial(
    json.dumps, cls=DatetimeAwareJSONEncoder, ensure_ascii=False
)

engine = create_async_engine(
    config.POSTGRES_URI,
    echo=config.POSTGRES_ECHO,
    future=True,
    isolation_level="READ COMMITTED",  # Не изменять
    json_serializer=custom_serializer,
    pool_pre_ping=True,
    pool_timeout=1,
    pool_size=10,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True
)

# convention - это набор правил для именования ограничений, связей и т.д.
# https://docs.sqlalchemy.org/en/14/core/constraints.html поиск по 'convention'
# значение меток-переменных:
# https://docs.sqlalchemy.org/en/14/core/metadata.html#sqlalchemy.schema.MetaData.params.naming_convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base: DeclarativeMeta = declarative_base(metadata=metadata)


# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# def get_session(function_):
#     """
#     Декоратор для получения сессии.
#     """
#     @wraps(function_)
#     async def wrapper(*args, **kwargs):
#         async with async_session() as session:
#             value = await function_(session=session, *args, **kwargs)
#         return value

#     return wrapper

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@asynccontextmanager
async def commit(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для commit.
    Проверяет, закрывается ли транзакция и если нет, то откатывает.
    Использовать только если много действий.
    Для одиночных действий использовать просто await session.commit().
    """
    try:
        if session.in_transaction():
            yield session

        else:
            async with session.begin():
                yield session

        await session.commit()

    except Exception as e:
        await session.rollback()
        raise e
