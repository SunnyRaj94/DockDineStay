# app/routers/boats.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from dockdinestay.db import Boat, BoatCRUD
from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.auth_utils import is_admin
from dockdinestay.routers.dependencies import get_boat_crud  # Import your dependency

router = APIRouter(
    prefix="/boats",
    tags=["Boats"],
)


@router.post(
    "/",
    response_model=Boat,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def create_boat(boat: Boat, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    created_boat = await boat_crud.create_boat(boat)
    return created_boat


@router.get(
    "/",
    response_model=List[Boat],
    summary="Get all boats (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_all_boats(boat_crud: BoatCRUD = Depends(get_boat_crud)):
    boats = await boat_crud.get_all_boats()
    return boats


@router.get(
    "/{boat_id}",
    response_model=Boat,
    summary="Get a boat by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_boat_by_id(boat_id: str, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    boat = await boat_crud.get_boat_by_id(boat_id)
    if boat:
        return boat
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found")


@router.put(
    "/{boat_id}",
    response_model=Boat,
    summary="Update an existing boat (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def update_boat(
    boat_id: str, boat: Boat, boat_crud: BoatCRUD = Depends(get_boat_crud)
):
    updated_boat = await boat_crud.update_boat(boat_id, boat)
    if updated_boat:
        return updated_boat
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found")


@router.delete(
    "/{boat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a boat (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def delete_boat(boat_id: str, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    deleted = await boat_crud.delete_boat(boat_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found"
        )
    return
