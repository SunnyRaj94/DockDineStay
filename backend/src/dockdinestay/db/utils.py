from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from typing import Any, Dict
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import AsyncMongoClient
from pydantic_core import CoreSchema, core_schema
import bcrypt
from dockdinestay.configs import env
from enum import Enum

# Ensure your MONGO_URI is correctly set up
MONGO_URI = env.get("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncMongoClient(MONGO_URI)  # Use AsyncIOMotorClient
db = client["DockDineStay"]


# --- Enums ---
class UserRole(str, Enum):
    ADMIN = "admin"
    FRONT_DESK = "front-desk"
    BACK_DESK = "back-desk"
    CUSTOMER = "customer"  # Added for completeness, if customers can have accounts


class HotelRoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


class HotelBookingStatus(str, Enum):
    BOOKED = "booked"
    CHECKED_IN = "checked-in"
    CHECKED_OUT = "checked-out"
    CANCELLED = "cancelled"
    PENDING = "pending"
    CHECKED_OUT_UNPAID = "checked-out-unpaid"


class CafeteriaTableStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    NEEDS_CLEANING = "needs_cleaning"


class CafeteriaOrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class BoatStatus(str, Enum):
    AVAILABLE = "available"
    ON_RENT = "on_rent"
    MAINTENANCE = "maintenance"
    DOCKED = "docked"  # Corrected case for consistency


class BoatBookingStatus(str, Enum):
    BOOKED = "booked"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# --- PyObjectId Helper for Pydantic v2 ---
class PyObjectId(ObjectId):
    """
    Custom type for MongoDB ObjectId to integrate with Pydantic v2.
    Handles validation from string/ObjectId and serialization to string.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        Pydantic v2 method to define the core validation and serialization schema.
        This tells Pydantic how to handle the type at runtime.
        """
        # The core schema for validation: it takes a string and validates it with `validate_and_return_id`
        validation_schema = core_schema.no_info_after_validator_function(
            cls.validate_and_return_id,
            core_schema.str_schema(),  # Expects a string input for validation
        )

        # Add serialization explicitly for the type itself
        # This creates a 'custom_type' schema that includes both the validation and serialization.
        return core_schema.json_or_python_schema(
            python_schema=validation_schema,
            json_schema=core_schema.str_schema(),  # For JSON, it should be a string
            serialization=core_schema.to_string_ser_schema(),  # Explicitly define how to serialize it
            # You can also add metadata here for better schema generation
            metadata={
                "pydantic.internal.is_instance_method": cls.validate_and_return_id
            },
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Dict[str, Any]:
        """
        Pydantic v2 method to define the JSON schema for OpenAPI docs.
        This represents the type as a string in the API documentation.
        """
        json_schema = handler(core_schema)
        json_schema.update(
            type="string", format="ObjectId", description="MongoDB ObjectId"
        )
        return json_schema

    @classmethod
    def validate_and_return_id(cls, v: Any) -> ObjectId:
        """
        Custom validator logic for PyObjectId.
        Accepts ObjectId instances or valid ObjectId strings.
        """
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId format")


# --- Utility Functions ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def default_time() -> datetime:
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)
