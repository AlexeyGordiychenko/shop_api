from datetime import datetime
from typing import List
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from shopAPI.models import (
    Order,
    OrderResponse,
    OrderResponseWithItems,
    OrderResponseWithItemsShort,
    Product,
    ProductResponse,
)


async def create_entities(client: AsyncClient, path: str, payloads: List[dict]) -> None:
    """
    Sends a POST request to the path with the payload.
    Validates the response and adds the received id to the payload.

    :param client: The test client.
    :param path: The path to send the request to.
    :param payloads: The payloads to send.
    :return: None
    """
    for payload in payloads:
        response_create = await client.post(
            path,
            json=payload,
        )
        assert response_create.status_code == 201
        response_create_json = response_create.json()
        assert "id" in response_create_json
        payload["id"] = response_create_json["id"]
        assert payload == response_create_json


async def get_product_from_db(id: str, db_session: AsyncSession) -> Product | None:
    """
    Returns a product from the database by id.
    If the product does not exist, returns None.

    :param id: The id to match.
    :param db_session: The database session.
    :return: The product instance.
    """
    return (
        await db_session.scalars(select(Product).where(Product.id == id))
    ).one_or_none()


async def compare_db_product_to_payload(
    product_payload: dict, db_session: AsyncSession
) -> None:
    """
    Compares a product from the database with the payload.

    :param product_payload: The payload to compare.
    :param db_session: The database session.
    :return: None
    """
    db_product = await get_product_from_db(product_payload["id"], db_session)
    assert db_product is not None
    assert (
        ProductResponse.model_validate(db_product).model_dump(mode="json")
        == product_payload
    )


async def compare_db_products_amount(
    products_amount: dict, db_session: AsyncSession
) -> None:
    """
    Compares the amount of products in the database
    with the amount in the products_amount dictionary.

    :param products_amount: The dictionary of products amount (id: amount).
    :param db_session: The database session.
    :return: None
    """
    db_products = (
        await db_session.scalars(
            select(Product).where(
                Product.id.in_([product_id for product_id in products_amount])
            )
        )
    ).all()
    assert len(db_products) == len(products_amount)
    for db_product in db_products:
        assert db_product.amount == products_amount[str(db_product.id)]


async def create_orders(client: AsyncClient, order_payloads: List[dict]) -> None:
    """
    Sends a POST request to the orders path with each payload.
    Validates the response and adds the received id, status and creation_date to the payload.

    :param client: The test client.
    :param order_payloads: The payloads to send.
    :return: None
    """
    for order_payload in order_payloads:
        response_create = await client.post("orders", json=order_payload)
        assert response_create.status_code == 201
        response_create_json = response_create.json()
        assert "id" in response_create_json
        assert "status" in response_create_json
        assert response_create_json["status"] == "created"
        assert "creation_date" in response_create_json
        assert (
            datetime.now()
            - datetime.strptime(
                response_create_json["creation_date"], "%Y-%m-%d %H:%M:%S"
            )
        ).total_seconds() < 10
        order_payload["id"] = response_create_json["id"]
        order_payload["status"] = response_create_json["status"]
        order_payload["creation_date"] = response_create_json["creation_date"]


async def get_order_from_db(id: str, db_session: AsyncSession) -> Order:
    """
    Returns an order from the database by id.
    If the order does not exist, returns None.

    :param id: The id to match.
    :param db_session: The database session.
    :return: The order instance.
    """
    return (
        await db_session.scalars(
            select(Order).where(Order.id == id).options(selectinload(Order.order_items))
        )
    ).one_or_none()


async def compare_db_order_to_payload(
    order_payload: dict, db_session: AsyncSession
) -> None:
    """
    Compares an order from the database with the payload.

    :param order_payload: The payload to compare.
    :param db_session: The database session.
    :return: None
    """
    db_order = await get_order_from_db(order_payload["id"], db_session)
    assert db_order is not None
    await compare_orders(order_payload, db_order)


async def compare_orders(
    expected: dict, actual: dict | Order, type: str = "items_short"
) -> None:
    """
    Compares two orders in a form of a dictionary.
    The type parameter determines the model to which the actual order will be transformed.

    :param expected: The expected order.
    :param actual: The actual order.
    :param type: The type of comparison. Can be "items_short", "items" or "base".
    :return: None
    """
    if type == "items_short":
        model = OrderResponseWithItemsShort
    elif type == "items":
        model = OrderResponseWithItems
    elif type == "base":
        model = OrderResponse
    else:
        raise ValueError("Wrong type")
    assert model.model_validate(actual).model_dump(mode="json") == expected


async def check_422_error(response: Response, field: str) -> None:
    """
    Checks if the response status code is 422
    and the error detail contains the field.

    :param response: The response to check.
    :param field: The field to check.
    :return: None
    """
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    detail = response_json["detail"]
    assert len(detail) == 1
    loc = detail[0]["loc"]
    assert isinstance(loc, list)
    assert loc[-1] == field
