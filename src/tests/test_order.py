from typing import List
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from shopAPI.models import OrderStatus
import tests.utils as utils


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [5, 1], indirect=True)
@pytest.mark.parametrize("order_payloads", [1, 3], indirect=True)
async def test_post_order(
    client: AsyncClient,
    order_payloads: List[dict],
    db_session: AsyncSession,
) -> None:
    await utils.create_orders(client, order_payloads)
    for order_payload in order_payloads:
        await utils.compare_db_order_to_payload(order_payload, db_session)


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [5, 1], indirect=True)
@pytest.mark.parametrize("order_payloads", [1, 3], indirect=True)
async def test_get_order(client: AsyncClient, order_payloads: List[dict]) -> None:
    await utils.create_orders(client, order_payloads)
    for order_payload in order_payloads:
        response_get = await client.get(f"orders/{order_payload['id']}")
        assert response_get.status_code == 200
        await utils.compare_orders(order_payload, response_get.json())


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [20, 1], indirect=True)
@pytest.mark.parametrize("order_payloads", [10, 15], indirect=True)
@pytest.mark.parametrize(
    "params", [{"limit": 3}, {"limit": 3, "offset": 4}, {"offset": 8}, {}]
)
async def test_get_all_orders_pagination(
    client: AsyncClient, order_payloads: List[dict], params: dict
) -> None:
    await utils.create_orders(client, order_payloads)
    offset = params.get("offset", 0)
    limit = params.get("limit", len(order_payloads) - offset)
    response_get = await client.get("orders/", params=params)
    assert response_get.status_code == 200
    response_get_json = response_get.json()
    assert len(response_get_json) == limit
    for i, order_payload in enumerate(order_payloads[offset : offset + limit]):
        await utils.compare_orders(order_payload, response_get_json[i])


@pytest.mark.asyncio
@pytest.mark.parametrize("product_payloads", [5], indirect=True)
@pytest.mark.parametrize("order_payloads", [2], indirect=True)
async def test_patch_order_status(
    client: AsyncClient, order_payloads: List[dict]
) -> None:
    await utils.create_orders(client, order_payloads)
    order_payload = order_payloads[0]
    for status in OrderStatus:
        order_payload["status"] = status
        response_patch = await client.patch(
            f"orders/{order_payload['id']}/status", params={"status": status.value}
        )
        await utils.compare_orders(response_patch.json(), order_payload, "base")
    response_get = await client.get(f"orders/{order_payloads[1]['id']}")
    assert response_get.status_code == 200
    await utils.compare_orders(order_payloads[1], response_get.json())
