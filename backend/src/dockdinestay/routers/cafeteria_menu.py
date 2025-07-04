# app/routers/cafeteria_menu.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from dockdinestay.db import CafeteriaOrderItem, CafeteriaOrderItemCRUD
from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.auth_utils import is_admin
from dockdinestay.routers.dependencies import (
    get_cafeteria_order_item_crud,
)

router = APIRouter(
    prefix="/menu-items",
    tags=["Cafeteria Menu Items"],
)


@router.post(
    "/",
    response_model=CafeteriaOrderItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria menu item (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def create_cafeteria_order_item(
    item: CafeteriaOrderItem,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    created_item = await item_crud.create_item(item)
    return created_item


@router.get(
    "/",
    response_model=List[CafeteriaOrderItem],
    summary="Get all cafeteria menu items (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_all_cafeteria_order_items(
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    items = await item_crud.get_all_items()
    return items


@router.get(
    "/{item_id}",
    response_model=CafeteriaOrderItem,
    summary="Get a cafeteria menu item by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_cafeteria_order_item_by_id(
    item_id: str,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    item = await item_crud.get_item_by_id(item_id)
    if item:
        return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria menu item not found"
    )


@router.put(
    "/{item_id}",
    response_model=CafeteriaOrderItem,
    summary="Update an existing cafeteria menu item (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def update_cafeteria_order_item(
    item_id: str,
    item: CafeteriaOrderItem,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    updated_item = await item_crud.update_item(item_id, item)
    if updated_item:
        return updated_item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria menu item not found"
    )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cafeteria menu item (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def delete_cafeteria_order_item(
    item_id: str,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    deleted = await item_crud.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafeteria menu item not found",
        )
    return
