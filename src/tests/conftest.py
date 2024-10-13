import random
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, List
import pytest
from httpx import AsyncClient, ASGITransport

from shopAPI.server import app
import shopAPI.database as database


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        base_url="http://testserver/api/v1/",
        transport=ASGITransport(app),
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with database.engine.connect() as connection:
        await connection.begin()
        session = database.prepare_session(connection)
        app.dependency_overrides[database.get_session] = lambda: session
        database.session = session
        yield session
        await session.close()
        await connection.rollback()

    await database.engine.dispose()
