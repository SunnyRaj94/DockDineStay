# app/dependencies.py

from fastapi import Depends
from dockdinestay.db import (
    db,
    UserCRUD,
    HotelRoomCRUD,
    HotelBookingCRUD,
    CafeteriaTableCRUD,
    CafeteriaOrderItemCRUD,
    CafeteriaOrderCRUD,
    BoatCRUD,
    BoatBookingCRUD,
)


# --- Dependencies for CRUD operations ---
def get_user_crud(database=Depends(lambda: db)) -> UserCRUD:
    return UserCRUD(database)


def get_hotel_room_crud(database=Depends(lambda: db)) -> HotelRoomCRUD:
    return HotelRoomCRUD(database)


def get_hotel_booking_crud(database=Depends(lambda: db)) -> HotelBookingCRUD:
    return HotelBookingCRUD(database)


def get_cafeteria_table_crud(database=Depends(lambda: db)) -> CafeteriaTableCRUD:
    return CafeteriaTableCRUD(database)


def get_cafeteria_order_item_crud(
    database=Depends(lambda: db),
) -> CafeteriaOrderItemCRUD:
    return CafeteriaOrderItemCRUD(database)


def get_cafeteria_order_crud(database=Depends(lambda: db)) -> CafeteriaOrderCRUD:
    return CafeteriaOrderCRUD(database)


def get_boat_crud(database=Depends(lambda: db)) -> BoatCRUD:
    return BoatCRUD(database)


def get_boat_booking_crud(database=Depends(lambda: db)) -> BoatBookingCRUD:
    return BoatBookingCRUD(database)
