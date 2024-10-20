from typing import List
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import tests.utils as utils


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads,", [1, 2], indirect=True)
async def test_post_product(
    client: AsyncClient,
    product_payloads: List[dict],
    db_session: AsyncSession,
) -> None:
    await utils.create_entities(client, "products", product_payloads)
    for product_payload in product_payloads:
        await utils.compare_db_product_to_payload(product_payload, db_session)


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1, 2], indirect=True)
async def test_get_product(client: AsyncClient, product_payloads: List[dict]) -> None:
    await utils.create_entities(client, "products", product_payloads)
    for product_payload in product_payloads:
        response_get = await client.get(f"products/{product_payload['id']}")
        assert response_get.status_code == 200
        assert response_get.json() == product_payload


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [10, 15], indirect=True)
@pytest.mark.parametrize(
    "params", [{"limit": 3}, {"limit": 3, "offset": 4}, {"offset": 8}, {}]
)
async def test_get_all_products_pagination(
    client: AsyncClient,
    product_payloads: List[dict],
    params: dict,
) -> None:
    await utils.create_entities(client, "products", product_payloads)
    offset = params.get("offset", 0)
    limit = params.get("limit", len(product_payloads) - offset)
    response_get = await client.get("products/", params=params)
    assert response_get.status_code == 200
    response_get_json = response_get.json()
    assert len(response_get_json) == limit
    for i, product_payload in enumerate(product_payloads[offset : offset + limit]):
        assert product_payload == response_get_json[i]


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [2], indirect=True)
async def test_put_product(
    client: AsyncClient,
    product_payloads: List[dict],
    db_session: AsyncSession,
) -> None:
    # Get two payloads, use one to create and the other to update
    updated_product = product_payloads.pop()
    await utils.create_entities(client, "products", product_payloads)
    created_product = product_payloads[0]
    response_put = await client.put(
        f"products/{created_product['id']}", json=updated_product
    )
    updated_product["id"] = created_product["id"]
    assert response_put.status_code == 200
    assert response_put.json() == updated_product
    await utils.compare_db_product_to_payload(updated_product, db_session)


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1, 2], indirect=True)
async def test_delete_product(
    client: AsyncClient,
    product_payloads: List[dict],
    db_session: AsyncSession,
) -> None:
    await utils.create_entities(client, "products", product_payloads)
    for product_payload in product_payloads:
        response_delete = await client.delete(f"products/{product_payload['id']}")
        assert response_delete.status_code == 200
        response_delete_json = response_delete.json()
        assert "detail" in response_delete_json
        assert response_delete_json["detail"] == "Deleted successfully."
        assert (
            await utils.get_product_from_db(product_payload["id"], db_session) is None
        )
