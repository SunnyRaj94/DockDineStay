# app/routers/boat_bookings.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from dockdinestay.db import BoatBooking, BoatBookingCRUD, UserRole
from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.auth_utils import (
    get_current_user_id,
    get_current_user_payload,
    is_staff_or_admin,
)
from dockdinestay.routers.dependencies import (
    get_boat_booking_crud,
)  # Import your dependency

router = APIRouter(
    prefix="/boat-bookings",
    tags=["Boat Bookings"],
)


@router.post(
    "/",
    response_model=BoatBooking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat booking (Authenticated User)",
)
async def create_boat_booking(
    booking: BoatBooking,
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
    current_user_id: str = Depends(get_current_user_id),
):
    if str(booking.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create bookings for other users.",
        )
    created_booking = await booking_crud.create_booking(booking)
    return created_booking


@router.get(
    "/",
    response_model=List[BoatBooking],
    summary="Get all boat bookings (Admin/Staff Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_staff_or_admin)],
)
async def get_all_boat_bookings(
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
):
    bookings = await booking_crud.get_all_bookings()
    return bookings


@router.get(
    "/{booking_id}",
    response_model=BoatBooking,
    summary="Get a boat booking by ID (Admin/Staff or Self)",
    dependencies=[Depends(JWTBearer())],  # Add JWTBearer here
)
async def get_boat_booking_by_id(
    booking_id: str,
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    booking = await booking_crud.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat booking not found"
        )

    # Note: Ensure UserRole.CUSTOMER is compared with .value if the payload role is a string
    if (
        current_user_payload["role"]
        == UserRole.CUSTOMER.value  # Corrected comparison to CUSTOMER
        and str(booking.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this booking.",
        )

    return booking


@router.put(
    "/{booking_id}",
    response_model=BoatBooking,
    summary="Update an existing boat booking (Admin/Staff or Self)",
    dependencies=[Depends(JWTBearer())],  # One JWTBearer is sufficient
)
async def update_boat_booking(
    booking_id: str,
    booking: BoatBooking,
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    current_booking = await booking_crud.get_booking_by_id(booking_id)
    if not current_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat booking not found"
        )

    # Note: Ensure UserRole.CUSTOMER is compared with .value if the payload role is a string
    if (
        current_user_payload["role"]
        == UserRole.CUSTOMER.value  # Corrected comparison to CUSTOMER
        and str(current_booking.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this booking.",
        )

    if (
        current_user_payload["role"] == UserRole.CUSTOMER.value
    ):  # Corrected comparison to CUSTOMER
        allowed_fields = {
            "notes",
            "status",
        }

        update_data_keys = set(booking.model_dump(exclude_unset=True).keys())
        if not update_data_keys.issubset(allowed_fields):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guests can only update specific fields (notes, status).",
            )

        # Assuming 'booking.status' is an enum, and 'cancelled' is a valid value/member
        # This needs to be consistent with your BoatBookingStatus enum definition
        if (
            "status" in update_data_keys
            and booking.status != current_booking.status
            # Corrected comparison: access the .value for string comparison if status is a StrEnum
            and booking.status.value != "cancelled"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guests can only change booking status to 'cancelled'.",
            )

    updated_booking = await booking_crud.update_booking(booking_id, booking)
    if updated_booking:
        return updated_booking
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Boat booking not found"
    )


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a boat booking (Admin/Staff Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_staff_or_admin)],
)
async def delete_boat_booking(
    booking_id: str, booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud)
):
    deleted = await booking_crud.delete_booking(booking_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat booking not found"
        )
    return
