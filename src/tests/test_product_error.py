from typing import List
import pytest
from httpx import AsyncClient
from uuid_extensions import uuid7

import tests.utils as utils


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1], indirect=True)
@pytest.mark.parametrize(
    "invalid_field",
    [{"price": "text_price"}, {"amount": "text_amount"}],
)
async def test_post_product_invalid_field(
    client: AsyncClient,
    product_payloads: List[dict],
    invalid_field: dict,
) -> None:
    product_payload = product_payloads[0]
    product_payload.update(invalid_field)
    response_create = await client.post("products", json=product_payload)
    await utils.check_422_error(response_create, next(iter(invalid_field)))


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1], indirect=True)
@pytest.mark.parametrize(
    "field",
    (
        "name",
        "description",
        "price",
        "amount",
    ),
)
async def test_post_product_fields_absence(
    client: AsyncClient, product_payloads: List[dict], field: str
) -> None:
    product_payload = product_payloads[0]
    product_payload.pop(field)
    response_create = await client.post("products", json=product_payload)
    await utils.check_422_error(response_create, field)


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient) -> None:
    response_get = await client.get(f"products/{uuid7()}")
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_get_product_incorrect_uuid(client: AsyncClient) -> None:
    response_get = await client.get("products/123")
    await utils.check_422_error(response_get, "id")


@pytest.mark.asyncio
@pytest.mark.parametrize("params", [{"limit": "limit"}, {"offset": "offset"}])
async def test_get_all_products_offset_limit(client: AsyncClient, params: dict) -> None:
    response_get = await client.get("products/", params=params)
    await utils.check_422_error(response_get, next(iter(params)))


@pytest.mark.asyncio
async def test_put_product_incorrect_uuid(client: AsyncClient) -> None:
    response_put = await client.put("products/123", json={"name": "test"})
    await utils.check_422_error(response_put, "id")


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1], indirect=True)
@pytest.mark.parametrize(
    "invalid_field",
    [{"price": "text_price"}, {"amount": "text_amount"}],
)
async def test_put_product_invalid_field(
    client: AsyncClient, product_payloads: List[dict], invalid_field: dict
) -> None:
    await utils.create_entities(client, "products", product_payloads)
    created_product = product_payloads[0]
    response_put = await client.put(
        f"products/{created_product['id']}", json=invalid_field
    )
    await utils.check_422_error(response_put, next(iter(invalid_field)))


@pytest.mark.asyncio
async def test_delete_product_not_found(client: AsyncClient) -> None:
    response_delete = await client.delete(f"products/{uuid7()}")
    assert response_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_incorrect_uuid(client: AsyncClient) -> None:
    response_delete = await client.delete("products/123")
    await utils.check_422_error(response_delete, "id")
