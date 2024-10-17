from typing import List, Optional
from fastapi import APIRouter, Query, status, Depends

from shopAPI.crud import ProductCRUD
from shopAPI.dependencies import valid_product_id
from shopAPI.models import (
    Product,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ResponseMessage,
)

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "/",
    summary="Create a new product.",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductResponse,
)
async def create_product(
    data: ProductCreate, crud: ProductCRUD = Depends()
) -> ProductResponse:
    return await crud.create(data)


@router.get(
    "/",
    summary="Get all products with pagination.",
    status_code=status.HTTP_200_OK,
    response_model=List[ProductResponse],
)
async def get_products_all(
    offset: int = Query(0, ge=0, description="Offset for pagination."),
    limit: int = Query(100, gt=0, le=100, description="Number of items to return."),
    crud: ProductCRUD = Depends(),
) -> List[ProductResponse]:
    return await crud.get_all(offset=offset, limit=limit)


@router.get(
    "/{id}",
    summary="Get a product.",
    status_code=status.HTTP_200_OK,
    response_model=ProductResponse,
    responses={404: {"model": ResponseMessage}},
)
async def get_product(product: Product = Depends(valid_product_id)) -> ProductResponse:
    return product


@router.put(
    "/{id}",
    summary="Update a product.",
    status_code=status.HTTP_200_OK,
    response_model=ProductResponse,
    responses={404: {"model": ResponseMessage}},
)
async def update_product(
    data: ProductUpdate,
    product: Product = Depends(valid_product_id),
    crud: ProductCRUD = Depends(),
) -> ProductResponse:
    return await crud.update(product, data)


@router.delete(
    "/{id}",
    summary="Delete a product.",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ResponseMessage],
    responses={404: {"model": ResponseMessage}},
)
async def delete_product(
    product: Product = Depends(valid_product_id),
    crud: ProductCRUD = Depends(),
) -> Optional[ResponseMessage]:
    await crud.delete(product)
    return ResponseMessage(detail="Deleted successfully.")
