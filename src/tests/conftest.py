import random
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, List
import pytest
from httpx import AsyncClient, ASGITransport

from shopAPI.server import app
import shopAPI.database as database
import tests.utils as utils


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


@pytest.fixture(scope="function")
def product_payloads(request: pytest.FixtureRequest) -> List[dict]:
    return [
        {
            "name": f"test_name_{i}",
            "description": f"test_description_{i}",
            "price": round(random.uniform(0, 1000), 2),
            "amount": random.randint(0, 1000),
        }
        for i in range(request.param)
    ]


@pytest.fixture(scope="function")
async def order_payloads(
    client: AsyncClient, request: pytest.FixtureRequest, product_payloads: List[dict]
) -> List[dict]:
    await utils.create_entities(client, "products", product_payloads)
    order_payloads = []
    for _ in range(request.param):
        selected_product_payloads = random.sample(
            product_payloads, random.randint(1, len(product_payloads))
        )
        order_payloads.append(
            {
                "order_items": [
                    {
                        "product_id": product_payload["id"],
                        "amount": random.randint(1, 1000),
                    }
                    for product_payload in selected_product_payloads
                ]
            }
        )
    return order_payloads
