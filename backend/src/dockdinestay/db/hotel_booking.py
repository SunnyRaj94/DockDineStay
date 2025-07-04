from typing import List, Optional
from bson import ObjectId
from pymongo import AsyncMongoClient
from fastapi import HTTPException, status
from dockdinestay.db.utils import (
    default_time,
    PyObjectId,
    HotelBookingStatus,
    HotelRoomStatus,
)


from datetime import datetime


from dockdinestay.db.models import HotelBooking


class HotelBookingCRUD:
    """
    CRUD operations for the HotelBooking collection.
    Handles dependencies on User and HotelRoom collections for validation.
    """

    def __init__(self, database: AsyncMongoClient):
        self.collection = database.hotel_bookings
        self.users_collection = database.users  # For user_id validation
        self.rooms_collection = (
            database.hotel_rooms
        )  # For room_id validation and status check

    async def _process_hotel_booking_doc(self, booking_doc: dict) -> HotelBooking:
        """
        Helper method to process raw MongoDB document before Pydantic validation.
        Ensures _id (ObjectId) is converted to string for PyObjectId.
        """
        if (
            booking_doc
            and "_id" in booking_doc
            and isinstance(booking_doc["_id"], ObjectId)
        ):
            booking_doc["id"] = str(booking_doc["_id"])
            booking_doc["room_id"] = str(booking_doc["room_id"])
            booking_doc["created_by"] = str(booking_doc["created_by"])
            del booking_doc["_id"]
        return HotelBooking.model_validate(booking_doc)

    async def _check_room_availability(
        self,
        room_id: PyObjectId,
        check_in: datetime,
        check_out: datetime,
        exclude_booking_id: Optional[PyObjectId] = None,
    ) -> bool:
        """
        Checks if a specific room is available for the given dates.
        Considers existing bookings for the same room.
        exclude_booking_id is used during updates to ignore the current booking.
        """
        # Ensure check_in and check_out are timezone-aware for comparison if your DB dates are.
        # If default_time() ensures UTC, convert incoming dates to UTC as well.
        check_in_utc = check_in.astimezone(
            datetime.now(check_in.tzinfo).tzinfo
        )  # Convert to timezone-aware based on input tz
        check_out_utc = check_out.astimezone(datetime.now(check_out.tzinfo).tzinfo)

        if check_in_utc >= check_out_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date.",
            )

        # Check if the room exists and is not 'out_of_service'
        room_doc = await self.rooms_collection.find_one({"_id": room_id})
        if not room_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Hotel room not found."
            )

        # Validate that the room is not 'OUT_OF_SERVICE'
        if room_doc.get("status") == HotelRoomStatus.MAINTENANCE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room {room_doc.get('room_number')} is out of service and cannot be booked.",
            )

        # Find existing bookings for this room that overlap with the new booking dates
        # Overlap occurs if:
        # (StartA <= EndB) AND (EndA >= StartB)
        # For bookings: (check_in <= existing_check_out) AND (check_out >= existing_check_in)

        # Active statuses that would block a new booking
        active_booking_statuses = [
            HotelBookingStatus.PENDING,
            HotelBookingStatus.BOOKED,
            HotelBookingStatus.CHECKED_IN,
            HotelBookingStatus.CHECKED_OUT_UNPAID,  # Room might still be considered occupied until payment settled
        ]

        query = {
            "room_id": room_id,
            "status": {"$in": active_booking_statuses},
            "check_in_date": {
                "$lt": check_out_utc
            },  # Existing booking starts before new booking ends
            "check_out_date": {
                "$gt": check_in_utc
            },  # Existing booking ends after new booking starts
        }

        if exclude_booking_id:
            query["_id"] = {
                "$ne": exclude_booking_id
            }  # Exclude the current booking itself during an update

        overlapping_bookings_count = await self.collection.count_documents(query)

        return overlapping_bookings_count == 0

    async def create_booking(self, booking_data: HotelBooking) -> HotelBooking:
        """
        Creates a new hotel booking.
        Validates user_id, room_id, and room availability.
        """
        # 1. Validate user_id
        user_doc = await self.users_collection.find_one(
            {"_id": booking_data.created_by}
        )
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        # 2. Validate room_id and availability
        room_available = await self._check_room_availability(
            booking_data.room_id,
            booking_data.check_in,
            booking_data.check_out,
        )
        if not room_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The selected room is not available for the specified dates.",
            )

        # Set default status, created_at, updated_at if not provided
        if not booking_data.status:
            booking_data.status = HotelBookingStatus.PENDING  # Default for new booking
        if not booking_data.created_at:
            booking_data.created_at = default_time()
        if not booking_data.updated_at:
            booking_data.updated_at = default_time()

        booking_dict = booking_data.model_dump(by_alias=True, exclude_unset=True)
        insert_result = await self.collection.insert_one(booking_dict)

        created_booking_doc = await self.collection.find_one(
            {"_id": insert_result.inserted_id}
        )
        if created_booking_doc:
            return await self._process_hotel_booking_doc(created_booking_doc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create hotel booking",
        )

    async def get_all_bookings(self) -> List[HotelBooking]:
        """
        Retrieves all hotel bookings.
        """
        bookings = []
        async for booking_doc in self.collection.find():
            bookings.append(await self._process_hotel_booking_doc(booking_doc))
        return bookings

    async def get_booking_by_id(self, booking_id: str) -> Optional[HotelBooking]:
        """
        Retrieves a single hotel booking by its ID.
        """
        if not ObjectId.is_valid(booking_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ObjectId format",
            )

        booking_doc = await self.collection.find_one({"_id": ObjectId(booking_id)})
        if booking_doc:
            return await self._process_hotel_booking_doc(booking_doc)
        return None

    async def update_booking(
        self, booking_id: str, booking_data: HotelBooking
    ) -> Optional[HotelBooking]:
        """
        Updates an existing hotel booking's information.
        Re-validates room availability if dates or room_id change.
        """
        if not ObjectId.is_valid(booking_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ObjectId format",
            )

        current_booking_doc = await self.collection.find_one(
            {"_id": ObjectId(booking_id)}
        )
        if not current_booking_doc:
            return None  # Booking not found

        update_data = booking_data.model_dump(by_alias=True, exclude_unset=True)
        update_data.pop("_id", None)
        update_data.pop("id", None)

        # If room_id or dates are being updated, re-check availability
        room_id_changed = update_data.get("room_id") and update_data[
            "room_id"
        ] != current_booking_doc.get("room_id")
        check_in_changed = update_data.get("check_in_date") and update_data[
            "check_in_date"
        ] != current_booking_doc.get("check_in_date")
        check_out_changed = update_data.get("check_out_date") and update_data[
            "check_out_date"
        ] != current_booking_doc.get("check_out_date")

        if room_id_changed or check_in_changed or check_out_changed:
            new_room_id = update_data.get("room_id", current_booking_doc["room_id"])
            new_check_in = update_data.get(
                "check_in_date", current_booking_doc["check_in_date"]
            )
            new_check_out = update_data.get(
                "check_out_date", current_booking_doc["check_out_date"]
            )

            room_available = await self._check_room_availability(
                new_room_id,
                new_check_in,
                new_check_out,
                exclude_booking_id=ObjectId(
                    booking_id
                ),  # Exclude the current booking from overlap check
            )
            if not room_available:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The selected room is not available for the updated dates.",
                )

        # User ID cannot be changed in a booking; it's linked to the initial creator
        if (
            "user_id" in update_data
            and update_data["user_id"] != current_booking_doc["user_id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID cannot be changed in a booking.",
            )

        # Update updated_at timestamp
        update_data["updated_at"] = default_time()

        result = await self.collection.update_one(
            {"_id": ObjectId(booking_id)}, {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="Booking data not modified",
            )

        updated_booking_doc = await self.collection.find_one(
            {"_id": ObjectId(booking_id)}
        )
        if updated_booking_doc:
            return await self._process_hotel_booking_doc(updated_booking_doc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated booking",
        )

    async def delete_booking(self, booking_id: str) -> bool:
        """
        Deletes a hotel booking from the database by its ID.
        Returns True if deleted, False if not found.
        """
        if not ObjectId.is_valid(booking_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ObjectId format",
            )

        delete_result = await self.collection.delete_one({"_id": ObjectId(booking_id)})
        return delete_result.deleted_count > 0
