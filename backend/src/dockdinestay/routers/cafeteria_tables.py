# app/routers/cafeteria_tables.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from dockdinestay.db import CafeteriaTable, CafeteriaTableCRUD
from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.auth_utils import is_admin, is_staff_or_admin
from dockdinestay.routers.dependencies import (
    get_cafeteria_table_crud,
)

router = APIRouter(
    prefix="/tables",
    tags=["Cafeteria Tables"],
)


@router.post(
    "/",
    response_model=CafeteriaTable,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria table (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def create_cafeteria_table(
    table: CafeteriaTable,
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    created_table = await table_crud.create_table(table)
    return created_table


@router.get(
    "/",
    response_model=List[CafeteriaTable],
    summary="Get all cafeteria tables (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_all_cafeteria_tables(
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    tables = await table_crud.get_all_tables()
    return tables


@router.get(
    "/{table_id}",
    response_model=CafeteriaTable,
    summary="Get a cafeteria table by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_cafeteria_table_by_id(
    table_id: str, table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud)
):
    table = await table_crud.get_table_by_id(table_id)
    if table:
        return table
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria table not found"
    )


@router.put(
    "/{table_id}",
    response_model=CafeteriaTable,
    summary="Update an existing cafeteria table (Admin/Staff Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_staff_or_admin)],
)
async def update_cafeteria_table(
    table_id: str,
    table: CafeteriaTable,
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    updated_table = await table_crud.update_table(table_id, table)
    if updated_table:
        return updated_table
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria table not found"
    )


@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cafeteria table (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def delete_cafeteria_table(
    table_id: str, table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud)
):
    deleted = await table_crud.delete_table(table_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria table not found"
        )
    return
