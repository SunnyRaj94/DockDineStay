from typing import List, Optional
from bson import ObjectId
from pymongo import AsyncMongoClient
from fastapi import HTTPException, status
from dockdinestay.db.utils import default_time
from dockdinestay.db.models import HotelRoom


class HotelRoomCRUD:
    """
    CRUD operations for the HotelRoom collection.
    """

    def __init__(self, database: AsyncMongoClient):
        self.collection = database.hotel_rooms  # Access the 'hotel_rooms' collection

    async def _process_hotel_room_doc(self, room_doc: dict) -> HotelRoom:
        """
        Helper method to process raw MongoDB document before Pydantic validation.
        Ensures _id (ObjectId) is converted to string for PyObjectId.
        """
        if room_doc and "_id" in room_doc and isinstance(room_doc["_id"], ObjectId):
            room_doc["id"] = str(room_doc["_id"])
            del room_doc["_id"]
        return HotelRoom.model_validate(room_doc)

    async def create_room(self, room_data: HotelRoom) -> HotelRoom:
        """
        Creates a new hotel room in the database.
        Checks for duplicate room number.
        """

        # Check if room_number already exists
        if await self.collection.find_one({"room_number": room_data.room_number}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room number '{room_data.room_number}' already exists.",
            )

        room_dict = room_data.model_dump(by_alias=True, exclude_unset=True)
        insert_result = await self.collection.insert_one(room_dict)

        created_room_doc = await self.collection.find_one(
            {"_id": insert_result.inserted_id}
        )
        if created_room_doc:
            return await self._process_hotel_room_doc(created_room_doc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create hotel room",
        )

    async def get_all_rooms(self) -> List[HotelRoom]:
        """
        Retrieves all hotel rooms from the database.
        """
        rooms = []
        async for room_doc in self.collection.find():
            rooms.append(await self._process_hotel_room_doc(room_doc))
        return rooms

    async def get_room_by_id(self, room_id: str) -> Optional[HotelRoom]:
        """
        Retrieves a single hotel room by its ID.
        """
        if not ObjectId.is_valid(room_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ObjectId format",
            )

        room_doc = await self.collection.find_one({"_id": ObjectId(room_id)})
        if room_doc:
            return await self._process_hotel_room_doc(room_doc)
        return None

    async def update_room(
        self, room_id: str, room_data: HotelRoom
    ) -> Optional[HotelRoom]:
        """
        Updates an existing hotel room's information.
        """
        if not ObjectId.is_valid(room_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ObjectId format",
            )

        update_data = room_data.model_dump(by_alias=True, exclude_unset=True)
        update_data.pop("_id", None)  # Ensure _id is not updated
        update_data.pop("id", None)  # Ensure 'id' is not updated

        # Prevent changing room_number to an existing one (if room_number is in update_data)
        if "room_number" in update_data:
            existing_room = await self.collection.find_one(
                {
                    "room_number": update_data["room_number"],
                    "_id": {"$ne": ObjectId(room_id)},
                }
            )
            if existing_room:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room number '{update_data['room_number']}' already exists for another room.",
                )

        # Update updated_at timestamp
        update_data["updated_at"] = default_time()

        result = await self.collection.update_one(
            {"_id": ObjectId(room_id)}, {"$set": update_data}
        )

        if result.modified_count == 0:
            if not await self.collection.find_one({"_id": ObjectId(room_id)}):
                return None  # Room not found
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="Room data not modified",
            )

        updated_room_doc = await self.collection.find_one({"_id": ObjectId(room_id)})
        if updated_room_doc:
            return await self._process_hotel_room_doc(updated_room_doc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated room",
        )

    async def delete_room(self, room_id: str) -> bool:
        """
        Deletes a hotel room from the database by its ID.
        Returns True if deleted, False if not found.
        """
        if not ObjectId.is_valid(room_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ObjectId format",
            )

        delete_result = await self.collection.delete_one({"_id": ObjectId(room_id)})
        return delete_result.deleted_count > 0
