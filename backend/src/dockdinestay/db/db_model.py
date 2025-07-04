from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    field_validator,
    ValidationInfo,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import AsyncMongoClient
from pydantic_core import CoreSchema, core_schema
import bcrypt
from enum import Enum
from dockdinestay.configs import env

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


class CafeteriaTableStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    NEEDS_CLEANING = "needs_cleaning"


class CafeteriaOrderStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    PAID = "paid"
    CANCELLED = "cancelled"


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


# --- Schemas (Pydantic v2 Style) ---


# ---------- User Schema ----------
class User(BaseModel):
    # For _id, if not provided, a new PyObjectId (which is an ObjectId) is generated
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    username: str = Field(min_length=3, max_length=50)
    email: Optional[EmailStr] = None  # Pydantic's built-in email validation
    password: str  # This will store the hashed password
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=15)
    role: UserRole
    profile_pic: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,  # Allows creation with field names or aliases
        arbitrary_types_allowed=True,  # Required for custom types like PyObjectId
        json_schema_extra={
            "example": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "hashedpassword123",  # Placeholder, actual hash expected
                "name": "Test User",
                "phone": "9876543210",
                "role": "customer",
                "profile_pic": "http://example.com/pic.png",
                "is_active": True,
            }
        },
    )

    # Example of a field validator (if you wanted to enforce phone format, etc.)
    @field_validator("phone")
    @classmethod
    def validate_phone_format(cls, v: str) -> str:
        cleaned = ''.join(c for c in v if c.isdigit() or (c == '+' and v.index(c) == 0))
        if not cleaned:
            return None
        if not cleaned.startswith('+') and not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits or start with +")
        return cleaned
        # # Simple example: ensure all digits, no special chars
        # if not v.isdigit():
        #     raise ValueError("Phone number must contain only digits")
        # return v


# ---------- Hotel Room Schema ----------
class HotelRoom(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    room_number: str = Field(min_length=1, max_length=10)
    type: str = Field(description="e.g., 'Standard', 'Deluxe', 'Suite'")
    price: float = Field(gt=0)
    status: HotelRoomStatus = HotelRoomStatus.AVAILABLE
    features: List[str] = Field(default_factory=list)  # Corrected type hint and default
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "room_number": "101",
                "type": "Standard",
                "price": 2500.00,
                "status": "available",
                "features": ["AC", "TV"],
                "image_url": "http://example.com/room101.jpg",
            }
        },
    )


# ---------- Hotel Booking Schema ----------
class HotelBooking(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    customer_name: str = Field(min_length=2, max_length=100)
    customer_phone: Optional[str] = Field(None, min_length=6, max_length=20)
    room_id: PyObjectId  # Will be validated as PyObjectId
    check_in: datetime
    check_out: datetime
    number_of_guests: int = Field(1, gt=0, le=10)
    special_requests: Optional[str] = Field(None, max_length=500)
    total_price: float = Field(gt=0)
    status: HotelBookingStatus = HotelBookingStatus.BOOKED
    created_by: Optional[PyObjectId] = None  # Staff who created the booking
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "customer_name": "John Doe",
                "customer_phone": "+1234567890",
                "room_id": "507f1f77bcf86cd799439011",
                "check_in": "2023-12-01T14:00:00Z",
                "check_out": "2023-12-05T11:00:00Z",
                "number_of_guests": 2,
                "special_requests": "Need a baby crib",
                "total_price": 1200.00,
                "status": "booked",
            }
        },
    )

    @field_validator("check_out")
    @classmethod
    def check_out_after_check_in(cls, v: datetime, info: ValidationInfo) -> datetime:
        if "check_in" in info.data and v <= info.data["check_in"]:
            raise ValueError("Check-out date must be after check-in date")
        return v

    @field_validator("customer_phone")
    @classmethod
    def validate_phone_not_empty_string(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():  # Convert empty strings to None
            return None
        return v


# ---------- Cafeteria Table Schema ----------
class CafeteriaTable(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    table_number: str = Field(min_length=1, max_length=10)
    capacity: int = Field(gt=0, description="How many people can sit at the table")
    status: CafeteriaTableStatus = CafeteriaTableStatus.AVAILABLE
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {"table_number": "T1", "capacity": 4, "status": "available"}
        },
    )


# ---------- Cafeteria Order Item (Sub-schema) ----------
class CafeteriaOrderItem(BaseModel):
    item_name: str = Field(min_length=2)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    notes: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_name": "Coffee",
                "quantity": 2,
                "unit_price": 50.00,
                "notes": "With extra sugar",
            }
        },
    )


# ---------- Cafeteria Order Schema ----------
class CafeteriaOrder(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    table_id: PyObjectId  # Link to a CafeteriaTable
    items: List[CafeteriaOrderItem]  # List of sub-schemas
    total: float = Field(gt=0)
    status: CafeteriaOrderStatus = CafeteriaOrderStatus.PENDING
    created_by: Optional[PyObjectId] = None  # Staff who took the order
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "table_id": "507f1f77bcf86cd799439011",
                "items": [
                    {"item_name": "Sandwich", "quantity": 1, "unit_price": 150.0},
                    {"item_name": "Juice", "quantity": 1, "unit_price": 70.0},
                ],
                "total": 220.0,
                "status": "pending",
            }
        },
    )


# ---------- Boat Schema ----------
class Boat(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    boat_number: str = Field(min_length=1, max_length=10)
    name: Optional[str] = Field(None, description="e.g., 'Speedy Go', 'The Explorer'")
    capacity: int = Field(gt=0)
    status: BoatStatus = BoatStatus.AVAILABLE
    image_url: Optional[str] = None
    daily_rate: float = Field(gt=0)  # Price per day
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "boat_number": "B01",
                "name": "Sea Cruiser",
                "capacity": 8,
                "status": "available",
                "daily_rate": 5000.00,
            }
        },
    )


# ---------- Boat Booking Schema ----------
class BoatBooking(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    customer_name: str = Field(min_length=2, max_length=100)
    customer_phone: Optional[str] = Field(None, min_length=6, max_length=20)
    boat_id: PyObjectId
    start_time: datetime
    end_time: datetime
    price: float = Field(gt=0)
    status: BoatBookingStatus = BoatBookingStatus.BOOKED
    assigned_staff: Optional[PyObjectId] = None  # Staff (driver) assigned for the trip
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "customer_name": "Jane Smith",
                "customer_phone": "+1987654321",
                "boat_id": "507f1f77bcf86cd799439011",
                "start_time": "2023-12-10T09:00:00Z",
                "end_time": "2023-12-10T17:00:00Z",
                "price": 3000.00,
                "status": "booked",
                "assigned_staff": "507f1f77bcf86cd799439012",
            }
        },
    )

    @field_validator("end_time")
    @classmethod
    def end_time_after_start_time(cls, v: datetime, info: ValidationInfo) -> datetime:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("End time must be after start time")
        return v

    @field_validator("customer_phone")
    @classmethod
    def validate_phone_not_empty_string(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            return None
        return v


# HotelRoom
# HotelBooking
# CafeteriaTable
# CafeteriaOrderItem
# CafeteriaOrder
# Boat
# BoatBooking
