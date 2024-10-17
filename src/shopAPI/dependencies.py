from uuid import UUID
from fastapi import Depends, HTTPException
from shopAPI.crud import ProductCRUD
from shopAPI.models import Product


async def valid_product_id(
    id: UUID,
    crud: ProductCRUD = Depends(),
) -> Product:
    product = await crud.get_by_id(id=id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {id} not found.")

    return product
