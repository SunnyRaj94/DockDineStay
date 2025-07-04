from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    field_validator,
    ValidationInfo,
    AliasChoices,
)

from dockdinestay.db.utils import (
    default_time,
    PyObjectId,
    CafeteriaOrderStatus,
    CafeteriaTableStatus,
    HotelBookingStatus,
    HotelRoomStatus,
    UserRole,
    BoatBookingStatus,
    BoatStatus,
    ObjectId,
)
from typing import List, Optional
from datetime import datetime

model_config_defaults = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
    from_attributes=True,  # Enable ORM mode for seamless conversion
)


# ---------- User Schema ----------
class User(BaseModel):
    # id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    id: Optional[PyObjectId] = Field(
        default_factory=PyObjectId,
        validation_alias=AliasChoices("_id", "id"),  # Allow _id or id for input
        serialization_alias="id",  # Explicitly force 'id' for output JSON
    )
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
        json_encoders={ObjectId: str, PyObjectId: str},  # Explicitly include PyObjectId
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
        cleaned = "".join(c for c in v if c.isdigit() or (c == "+" and v.index(c) == 0))
        if not cleaned:
            return None
        if not cleaned.startswith("+") and not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits or start with +")
        return cleaned


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


class CafeteriaOrderItem(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    item_name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)  # Price per unit/item (menu price)
    category: Optional[str] = None  # e.g., "Breakfast", "Lunch", "Beverage", "Dessert"
    is_available: bool = True  # Whether it's currently on the menu
    created_at: datetime = Field(default_factory=default_time)
    updated_at: datetime = Field(default_factory=default_time)

    model_config = model_config_defaults
    model_config["json_schema_extra"] = {
        "example": {
            "item_name": "Chicken Biryani",
            "description": "A flavorful rice dish with chicken and spices.",
            "price": 250.00,
            "category": "Main Course",
            "is_available": True,
        }
    }


# Define the schema for an individual item *within* an order
# This holds the snapshot details of the item at the time of order
class OrderItemDetail(BaseModel):
    item_id: PyObjectId = Field(...)  # References CafeteriaOrderItem ID (the menu item)
    item_name: str = Field(...)  # Snapshot of the name
    quantity: int = Field(..., gt=0)
    price_at_time_of_order: float = Field(..., gt=0)  # Snapshot of the price per unit
    notes: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "item_id": "60c72b2f9b1e8a4d7c8b4569",
                "item_name": "Chicken Biryani",
                "quantity": 1,
                "price_at_time_of_order": 250.00,
                "notes": "Extra spicy",
            }
        },
    )


# Main CafeteriaOrder Schema
class CafeteriaOrder(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)
    user_id: PyObjectId = Field(...)  # References the User who placed the order
    table_id: PyObjectId = Field(...)  # References the CafeteriaTable (if applicable)
    items: List[OrderItemDetail] = Field(
        default_factory=list
    )  # List of order item details
    total_amount: float = Field(0.0, ge=0)  # Calculated by the backend
    status: CafeteriaOrderStatus = CafeteriaOrderStatus.PENDING  # Default status
    order_time: datetime = Field(default_factory=default_time)
    pickup_time: Optional[datetime] = None  # Or ready_time
    served_time: Optional[datetime] = (
        None  # Using served_time instead of delivery_time for cafeteria
    )
    updated_at: datetime = Field(default_factory=default_time)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": "60c72b2f9b1e8a4d7c8b4567",
                "table_id": "60c72b2f9b1e8a4d7c8b4568",
                "items": [
                    {
                        "item_id": "60c72b2f9b1e8a4d7c8b4569",
                        "item_name": "Chicken Biryani",
                        "quantity": 1,
                        "price_at_time_of_order": 250.00,
                    },
                    {
                        "item_id": "60c72b2f9b1e8a4d7c8b4570",
                        "item_name": "Coca Cola",
                        "quantity": 2,
                        "price_at_time_of_order": 50.00,
                        "notes": "No ice",
                    },
                ],
                "total_amount": 350.00,
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
