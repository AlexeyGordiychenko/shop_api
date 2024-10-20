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
    """
    Yields an async client for testing.
    """
    async with AsyncClient(
        base_url="http://testserver/api/v1/",
        transport=ASGITransport(app),
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a database session for testing.
    Rolls back the session at the end of the test.
    """
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
    """
    Generates a requested number of product payloads.
    Example of a payload:
        {
            "name": "test_name_0",
            "description": "test_description_0",
            "price": 10.0,
            "amount": 1000,
        }

    :param request: The fixture request (request.param is the number of product payloads).
    :return: A list of product payloads.
    """
    return [
        {
            "name": f"test_name_{i}",
            "description": f"test_description_{i}",
            "price": round(random.uniform(0, 1000), 2),
            "amount": random.randint(1000, 10000),
        }
        for i in range(request.param)
    ]


@pytest.fixture(scope="function")
async def order_payloads(
    client: AsyncClient, request: pytest.FixtureRequest, product_payloads: List[dict]
) -> List[dict]:
    """
    Creates products and generates a requested number of order payloads with products ids.
    Example of a payload:
        {
            "order_items": [
                {
                    "product_id": "067153e9-dc89-7044-8000-22822f938b66",
                    "amount": 10,
                }
            ]
        }

    :param request: The fixture request (request.param is the number of order payloads).
    :param product_payloads: The list of product payloads.
    :return: A list of order payloads.
    """
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
                        "amount": random.randint(
                            1, max(1, product_payload["amount"] // request.param)
                        ),
                    }
                    for product_payload in selected_product_payloads
                ]
            }
        )
    return order_payloads
