from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from shopAPI.models import (
    OrderCreate,
    OrderResponse,
    OrderResponseWithItems,
    OrderStatus,
    OrderStatusUpdate,
    ResponseMessage,
)
from shopAPI.crud import OrderCRUD

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    summary="Create a new order.",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse,
    responses={404: {"model": ResponseMessage}},
)
async def create_order(data: OrderCreate, crud: OrderCRUD = Depends()) -> OrderResponse:
    return await crud.create(data)


@router.get(
    "/",
    summary="Get all orders with pagination.",
    status_code=status.HTTP_200_OK,
    response_model=List[OrderResponseWithItems],
)
async def get_orders_all(
    offset: int = Query(0, ge=0, description="Offset for pagination."),
    limit: int = Query(100, gt=0, le=100, description="Number of items to return."),
    crud: OrderCRUD = Depends(),
) -> List[OrderResponseWithItems]:
    return await crud.get_all(offset=offset, limit=limit)


@router.get(
    "/{id}",
    summary="Get an order by id.",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponseWithItems,
    responses={404: {"model": ResponseMessage}},
)
async def get_order(id: UUID, crud: OrderCRUD = Depends()) -> OrderResponseWithItems:
    return await crud.get_by_id(id=id)


@router.patch(
    "/{id}/status",
    summary="Update order's status.",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponse,
)
async def update_order_status(
    id: UUID,
    status: OrderStatus = Query(
        description="New status.", examples=OrderStatus.shipped
    ),
    crud: OrderCRUD = Depends(),
) -> OrderResponse:
    return await crud.update(
        await crud.get_by_id(id=id), OrderStatusUpdate(status=status)
    )
