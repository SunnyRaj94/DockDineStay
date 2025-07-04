# app/routers/cafeteria_orders.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from dockdinestay.db import CafeteriaOrder, CafeteriaOrderCRUD, UserRole
from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.auth_utils import (
    get_current_user_id,
    get_current_user_payload,
    is_staff_or_admin,
)
from dockdinestay.routers.dependencies import get_cafeteria_order_crud

router = APIRouter(
    prefix="/orders",
    tags=["Cafeteria Orders"],
)


@router.post(
    "/",
    response_model=CafeteriaOrder,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria order (Authenticated User)",
)
async def create_cafeteria_order(
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
    current_user_id: str = Depends(get_current_user_id),
):
    if str(order.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create orders for other users.",
        )
    created_order = await order_crud.create_order(order)
    return created_order


@router.get(
    "/",
    response_model=List[CafeteriaOrder],
    summary="Get all cafeteria orders (Admin/Staff Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_staff_or_admin)],
)
async def get_all_cafeteria_orders(
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    orders = await order_crud.get_all_orders()
    return orders


@router.get(
    "/{order_id}",
    response_model=CafeteriaOrder,
    summary="Get a cafeteria order by ID (Admin/Staff or Self)",
    dependencies=[Depends(JWTBearer())],  # Add JWTBearer here
)
async def get_cafeteria_order_by_id(
    order_id: str,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    order = await order_crud.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
        )

    # Note: Ensure UserRole.CUSTOMER is compared with .value if the payload role is a string
    if (
        current_user_payload["role"]
        == UserRole.CUSTOMER.value  # Corrected comparison to CUSTOMER
        and str(order.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this order.",
        )

    return order


@router.put(
    "/{order_id}",
    response_model=CafeteriaOrder,
    summary="Update an existing cafeteria order (Admin/Staff or Self)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def update_cafeteria_order(
    order_id: str,
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    current_order = await order_crud.get_order_by_id(order_id)
    if not current_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
        )

    # Note: Ensure UserRole.CUSTOMER is compared with .value if the payload role is a string
    if (
        current_user_payload["role"]
        == UserRole.CUSTOMER.value  # Corrected comparison to CUSTOMER
        and str(current_order.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this order.",
        )

    if (
        current_user_payload["role"] == UserRole.CUSTOMER.value
    ):  # Corrected comparison to CUSTOMER
        # Assuming you have a 'status' field in your CafeteriaOrder model that is an Enum
        # You'll need to define OrderStatus enum in your models similar to how HotelBookingStatus is defined
        # If order.status is an enum, compare its value
        # Ensure 'cancelled' is a valid status in your CafeteriaOrderStatus enum
        if (
            "status" in order.model_dump(exclude_unset=True)
            and order.status != current_order.status
            # Replace current_order.status.cancelled with the actual Enum member or its .value
            # For example, if you have CafeteriaOrderStatus.CANCELLED
            # and order.status.value != CafeteriaOrderStatus.CANCELLED.value
            # Or if it's a simple string, then just 'cancelled'
            # For now, I'm assuming 'order.status.cancelled' is not a valid enum access.
            # This line needs review based on your actual CafeteriaOrderStatus enum.
            # For consistency, I'll use `order.status.value` assuming it's a StrEnum
            and order.status.value
            != "cancelled"  # <-- Assuming "cancelled" is the string value for cancellation
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guests can only change order status to 'cancelled'.",
            )

    updated_order = await order_crud.update_order(order_id, order)
    if updated_order:
        return updated_order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
    )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cafeteria order (Admin/Staff Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_staff_or_admin)],
)
async def delete_cafeteria_order(
    order_id: str, order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud)
):
    deleted = await order_crud.delete_order(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
        )
    return
