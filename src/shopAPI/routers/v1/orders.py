from typing import List
from fastapi import APIRouter, Depends, Query, status

from shopAPI.crud import OrderCRUD
from shopAPI.dependencies import valid_order_id
from shopAPI.models import (
    Order,
    OrderCreate,
    OrderResponse,
    OrderResponseWithItems,
    OrderStatus,
    OrderStatusUpdate,
    ResponseMessage,
)

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
async def get_order(
    order: Order = Depends(valid_order_id), crud: OrderCRUD = Depends()
) -> OrderResponseWithItems:
    return order


@router.patch(
    "/{id}/status",
    summary="Update order's status.",
    status_code=status.HTTP_200_OK,
    response_model=OrderResponse,
    responses={404: {"model": ResponseMessage}},
)
async def update_order_status(
    status: OrderStatus = Query(
        description="New status.", examples=OrderStatus.shipped
    ),
    order: Order = Depends(valid_order_id),
    crud: OrderCRUD = Depends(),
) -> OrderResponse:
    return await crud.update(order, OrderStatusUpdate(status=status))
