from typing import List
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from shopAPI.models import Product, ProductResponse


async def create_entities(
    client: AsyncClient, path: str, payloads: List[dict]
) -> List[dict]:
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


async def get_product_from_db(id: str, db_session: AsyncSession) -> Product:
    return (
        await db_session.scalars(select(Product).where(Product.id == id))
    ).one_or_none()


async def compare_db_product_to_payload(
    product_payload: dict, db_session: AsyncSession
) -> None:
    db_product = await get_product_from_db(product_payload["id"], db_session)
    assert db_product is not None
    assert (
        ProductResponse.model_validate(db_product).model_dump(mode="json")
        == product_payload
    )


async def check_422_error(response: Response, field: str) -> None:
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    detail = response_json["detail"]
    assert len(detail) == 1
    loc = detail[0]["loc"]
    assert isinstance(loc, list)
    assert loc[-1] == field
