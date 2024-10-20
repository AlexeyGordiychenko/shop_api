from asyncio import current_task
from functools import wraps
from typing import AsyncGenerator, Union
from uuid import UUID
from uuid_extensions import uuid7

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncConnection,
)
from sqlmodel import Field, SQLModel

from shopAPI.config import settings


class IdMixin(SQLModel):
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )


class Transactional:
    def __init__(self, refresh: bool = False):
        self.refresh = refresh

    def __call__(self, function):
        @wraps(function)
        async def decorator(*args, **kwargs):
            try:
                result = await function(*args, **kwargs)
                await session.commit()
                if self.refresh:
                    await session.refresh(result)
                return result
            except Exception as exception:
                await session.rollback()
                raise exception

        return decorator


def prepare_session(bind: Union[AsyncEngine, AsyncConnection]) -> AsyncSession:
    async_session_factory = async_sessionmaker(
        bind=bind,
        expire_on_commit=False,
    )
    session = async_scoped_session(
        session_factory=async_session_factory,
        scopefunc=current_task,
    )

    return session


engine = create_async_engine(
    str(settings.DB_URI),
    echo=settings.DB_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
)

session = prepare_session(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get the database session.
    This can be used for dependency injection.

    :return: The database session.
    """
    try:
        yield session
    finally:
        await session.close()
