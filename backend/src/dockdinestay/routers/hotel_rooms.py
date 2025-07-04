# app/routers/hotel_rooms.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from dockdinestay.db import HotelRoom, HotelRoomCRUD
from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.auth_utils import is_admin

from dockdinestay.routers.dependencies import get_hotel_room_crud

router = APIRouter(
    prefix="/rooms",
    tags=["Hotel Rooms"],
)


@router.post(
    "/",
    response_model=HotelRoom,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel room (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def create_hotel_room(
    room: HotelRoom, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    created_room = await room_crud.create_room(room)
    return created_room


@router.get(
    "/",
    response_model=List[HotelRoom],
    summary="Get all hotel rooms (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_all_hotel_rooms(room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)):
    rooms = await room_crud.get_all_rooms()
    return rooms


@router.get(
    "/{room_id}",
    response_model=HotelRoom,
    summary="Get a hotel room by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def get_hotel_room_by_id(
    room_id: str, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    room = await room_crud.get_room_by_id(room_id)
    if room:
        return room
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Hotel room not found"
    )


@router.put(
    "/{room_id}",
    response_model=HotelRoom,
    summary="Update an existing hotel room (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def update_hotel_room(
    room_id: str,
    room: HotelRoom,
    room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud),
):
    updated_room = await room_crud.update_room(room_id, room)
    if updated_room:
        return updated_room
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Hotel room not found"
    )


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hotel room (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def delete_hotel_room(
    room_id: str, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    deleted = await room_crud.delete_room(room_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel room not found"
        )
    return
