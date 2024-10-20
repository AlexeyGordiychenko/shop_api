from typing import List
import pytest
from httpx import AsyncClient
from uuid_extensions import uuid7

from shopAPI.models import OrderStatus
import tests.utils as utils


@pytest.mark.asyncio
async def test_post_order_empty(
    client: AsyncClient,
) -> None:
    response_create = await client.post("orders", json={})
    await utils.check_422_error(response_create, "order_items")


@pytest.mark.asyncio
async def test_post_order_items_empty(
    client: AsyncClient,
) -> None:
    response_create = await client.post("orders", json={"order_items": []})
    await utils.check_422_error(response_create, "order_items")


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1], indirect=True)
@pytest.mark.parametrize("order_payloads", [1], indirect=True)
@pytest.mark.parametrize(
    "invalid_field",
    [{"product_id": "123"}, {"amount": 0}, {"amount": -1}, {"amount": -1234}],
)
async def test_post_order_items_invalid_field(
    client: AsyncClient, order_payloads: List[dict], invalid_field: dict
) -> None:
    order_payload = order_payloads[0]
    order_payload["order_items"][0].update(invalid_field)
    response_create = await client.post("orders", json=order_payload)
    await utils.check_422_error(response_create, next(iter(invalid_field)))


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1], indirect=True)
@pytest.mark.parametrize("order_payloads", [1], indirect=True)
@pytest.mark.parametrize("field", ("product_id", "amount"))
async def test_post_order_items_field_absence(
    client: AsyncClient, order_payloads: List[dict], field: str
) -> None:
    order_payload = order_payloads[0]
    order_payload["order_items"][0].pop(field)
    response_create = await client.post("orders", json=order_payload)
    await utils.check_422_error(response_create, field)


@pytest.mark.asyncio
async def test_post_order_product_id_not_found(
    client: AsyncClient,
) -> None:
    product_id = str(uuid7())
    order_payload = {"order_items": [{"product_id": product_id, "amount": 1}]}
    response_create = await client.post("orders", json=order_payload)
    assert response_create.status_code == 404
    response_create_json = response_create.json()
    assert "detail" in response_create_json
    assert response_create_json["detail"] == f"Product {product_id} not found."


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [1], indirect=True)
@pytest.mark.parametrize("order_payloads", [1], indirect=True)
async def test_post_order_products_amount_not_in_stock(
    client: AsyncClient, product_payloads: List[dict], order_payloads: List[dict]
) -> None:
    order_payload = order_payloads[0]
    product_payload = product_payloads[0]
    order_payload["order_items"][0]["amount"] = product_payload["amount"] + 1
    response_create = await client.post("orders", json=order_payload)
    assert response_create.status_code == 400
    response_create_json = response_create.json()
    assert "detail" in response_create_json
    assert (
        response_create_json["detail"]
        == f"Product {product_payload['id']} not enough in stock."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [5], indirect=True)
@pytest.mark.parametrize("order_payloads", [1], indirect=True)
async def test_post_order_duplicate_products(
    client: AsyncClient, order_payloads: List[dict]
) -> None:
    order_payload = order_payloads[0]
    order_payload["order_items"].append(order_payload["order_items"][0])
    response_create = await client.post("orders", json=order_payload)
    assert response_create.status_code == 400
    response_create_json = response_create.json()
    assert "detail" in response_create_json
    assert response_create_json["detail"] == "Duplicate product IDs."


@pytest.mark.asyncio
async def test_get_order_not_found(client: AsyncClient) -> None:
    response_get = await client.get(f"orders/{uuid7()}")
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_get_order_incorrect_uuid(client: AsyncClient) -> None:
    response_get = await client.get("orders/123")
    await utils.check_422_error(response_get, "id")


@pytest.mark.asyncio
@pytest.mark.parametrize("params", [{"limit": "limit"}, {"offset": "offset"}])
async def test_get_all_orders_offset_limit(client: AsyncClient, params: dict) -> None:
    response_get = await client.get("orders/", params=params)
    await utils.check_422_error(response_get, next(iter(params)))


@pytest.mark.asyncio
async def test_patch_order_status_not_found(client: AsyncClient) -> None:
    response_patch = await client.patch(
        f"orders/{uuid7()}/status", params={"status": OrderStatus.created.value}
    )
    assert response_patch.status_code == 404


@pytest.mark.asyncio
async def test_patch_order_status_incorrect_uuid(client: AsyncClient) -> None:
    response_patch = await client.patch(
        "orders/123/status", params={"status": OrderStatus.created.value}
    )
    await utils.check_422_error(response_patch, "id")


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [5], indirect=True)
@pytest.mark.parametrize("order_payloads", [1], indirect=True)
@pytest.mark.parametrize("params", [{"status": "test_status"}, {}])
async def test_patch_order_status_incorrect_status(
    client: AsyncClient, order_payloads: List[dict], params: dict
) -> None:
    await utils.create_orders(client, order_payloads)
    response_patch = await client.patch(
        f"orders/{order_payloads[0]['id']}/status",
        params=params,
    )
    await utils.check_422_error(response_patch, "status")
