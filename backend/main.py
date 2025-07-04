from fastapi import FastAPI, HTTPException, status, Depends
from typing import List
from fastapi.security import OAuth2PasswordRequestForm

from dockdinestay.db import (
    User,
    UserRole,
    db,
    UserCRUD,
    HotelRoom,
    HotelRoomCRUD,
    HotelBooking,
    HotelBookingCRUD,
    CafeteriaTableCRUD,
    CafeteriaTable,
    CafeteriaOrderItem,
    CafeteriaOrderItemCRUD,
    CafeteriaOrderCRUD,
    CafeteriaOrder,
    Boat,
    BoatCRUD,
    BoatBookingCRUD,
    BoatBooking,
)

from dockdinestay.db.utils import verify_password, hash_password
from dockdinestay.auth.auth_utils import (
    get_current_user_payload,
    get_current_user_id,
    # get_current_user_role,
    is_admin,
    is_staff_or_admin,
    # has_role,
)

from dockdinestay.auth.auth_handler import create_access_token
from dockdinestay.auth.auth_bearer import JWTBearer

# from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.token import Token  # For the token response model


app = FastAPI(
    title="DockDineStay API",
    description="API for managing hotel rooms, bookings, cafeteria services, and boat rentals.",
    version="0.1.0",
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


# --- API Endpoints ---


@app.get("/", summary="Root endpoint")
async def read_root():
    return {"message": "Welcome to DockDineStay API!"}


# --- Authentication Endpoints ---
@app.post(
    "/token", response_model=Token, summary="Authenticate user and get access token"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    user_in_db = await user_crud.get_user_by_username(form_data.username)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token payload with subject (username), user_id, and role
    access_token_data = {
        "sub": user_in_db.username,
        "user_id": str(user_in_db.id),
        "role": user_in_db.role.value,
    }

    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}


# --- User Endpoints ---
@app.post(
    "/users/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Registration)",
)
async def create_user(user: User, user_crud: UserCRUD = Depends(get_user_crud)):
    # This endpoint is publicly accessible for new user registration
    user.hashed_password = hash_password(user.hashed_password)
    created_user = await user_crud.create_user(user)
    return created_user


@app.get(
    "/users/",
    response_model=List[User],
    summary="Get all users (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def get_all_users(user_crud: UserCRUD = Depends(get_user_crud)):
    users = await user_crud.get_all_users()
    return users


@app.get(
    "/users/me", response_model=User, summary="Get current authenticated user's profile"
)
async def get_current_user_profile(
    user_id: str = Depends(get_current_user_id),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    user = await user_crud.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found (should not happen for /me)",
    )


@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="Get a user by ID (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def get_user_by_id(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    user = await user_crud.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.put(
    "/users/{user_id}",
    response_model=User,
    summary="Update an existing user (Admin or Self)",
    dependencies=[Depends(JWTBearer())],
)
async def update_user(
    user_id: str,
    user: User,
    user_crud: UserCRUD = Depends(get_user_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    # Allow admin to update any user, or a user to update their own profile
    if (
        current_user_payload["role"] != UserRole.ADMIN.value
        and current_user_payload["user_id"] != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user.",
        )

    # If password is being updated, hash it
    if user.hashed_password:
        user.hashed_password = hash_password(user.hashed_password)
    updated_user = await user_crud.update_user(user_id, user)
    if updated_user:
        return updated_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def delete_user(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    deleted = await user_crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return


# --- Hotel Room Endpoints ---
@app.post(
    "/rooms/",
    response_model=HotelRoom,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel room (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def create_hotel_room(
    room: HotelRoom, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    created_room = await room_crud.create_room(room)
    return created_room


@app.get(
    "/rooms/",
    response_model=List[HotelRoom],
    summary="Get all hotel rooms (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_hotel_rooms(room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)):
    rooms = await room_crud.get_all_rooms()
    return rooms


@app.get(
    "/rooms/{room_id}",
    response_model=HotelRoom,
    summary="Get a hotel room by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
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


@app.put(
    "/rooms/{room_id}",
    response_model=HotelRoom,
    summary="Update an existing hotel room (Admin Only)",
    dependencies=[Depends(is_admin)],
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


@app.delete(
    "/rooms/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hotel room (Admin Only)",
    dependencies=[Depends(is_admin)],
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


# --- Hotel Booking Endpoints ---
@app.post(
    "/bookings/",
    response_model=HotelBooking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel booking (Authenticated User)",
)
async def create_hotel_booking(
    booking: HotelBooking,
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
    current_user_id: str = Depends(get_current_user_id),  # Get user ID from token
):
    # Ensure the booking is made by the authenticated user
    if str(booking.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create bookings for other users.",
        )
    created_booking = await booking_crud.create_booking(booking)
    return created_booking


@app.get(
    "/bookings/",
    response_model=List[HotelBooking],
    summary="Get all hotel bookings (Admin/Staff Only)",
    dependencies=[Depends(is_staff_or_admin)],
)
async def get_all_hotel_bookings(
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
):
    bookings = await booking_crud.get_all_bookings()
    return bookings


@app.get(
    "/bookings/{booking_id}",
    response_model=HotelBooking,
    summary="Get a hotel booking by ID (Admin/Staff or Self)",
)
async def get_hotel_booking_by_id(
    booking_id: str,
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    booking = await booking_crud.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel booking not found"
        )

    # Admin/Staff can view any booking, Guests can only view their own
    if (
        current_user_payload["role"] == UserRole.GUEST.value
        and str(booking.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this booking.",
        )

    return booking


@app.put(
    "/bookings/{booking_id}",
    response_model=HotelBooking,
    summary="Update an existing hotel booking (Admin/Staff or Self)",
    dependencies=[Depends(JWTBearer())],
)
async def update_hotel_booking(
    booking_id: str,
    booking: HotelBooking,
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    current_booking = await booking_crud.get_booking_by_id(booking_id)
    if not current_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel booking not found"
        )

    # Admin/Staff can update any booking, Guests can only update their own
    if (
        current_user_payload["role"] == UserRole.GUEST.value
        and str(current_booking.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this booking.",
        )

    # Guests can only update specific fields, e.g., notes, or cancel if allowed
    if current_user_payload["role"] == UserRole.GUEST.value:
        allowed_fields = {
            "notes",
            "status",
        }  # Example: allow guests to update notes or cancel status

        # Check if they are trying to change disallowed fields
        update_data_keys = set(booking.model_dump(exclude_unset=True).keys())
        if not update_data_keys.issubset(allowed_fields):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guests can only update specific fields (notes, status).",
            )

        # Specific check for status: guests might only be allowed to change to 'cancelled'
        if (
            "status" in update_data_keys
            and booking.status != current_booking.status
            and booking.status != current_booking.status.cancelled
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guests can only change booking status to 'cancelled'.",
            )

    updated_booking = await booking_crud.update_booking(booking_id, booking)
    if updated_booking:
        return updated_booking
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Hotel booking not found"
    )


@app.delete(
    "/bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hotel booking (Admin/Staff Only)",
    dependencies=[Depends(is_staff_or_admin)],
)
async def delete_hotel_booking(
    booking_id: str, booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud)
):
    deleted = await booking_crud.delete_booking(booking_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel booking not found"
        )
    return


# --- Cafeteria Table Endpoints ---
@app.post(
    "/tables/",
    response_model=CafeteriaTable,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria table (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def create_cafeteria_table(
    table: CafeteriaTable,
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    created_table = await table_crud.create_table(table)
    return created_table


@app.get(
    "/tables/",
    response_model=List[CafeteriaTable],
    summary="Get all cafeteria tables (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_cafeteria_tables(
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    tables = await table_crud.get_all_tables()
    return tables


@app.get(
    "/tables/{table_id}",
    response_model=CafeteriaTable,
    summary="Get a cafeteria table by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
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


@app.put(
    "/tables/{table_id}",
    response_model=CafeteriaTable,
    summary="Update an existing cafeteria table (Admin/Staff Only)",
    dependencies=[Depends(is_staff_or_admin)],
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


@app.delete(
    "/tables/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cafeteria table (Admin Only)",
    dependencies=[Depends(is_admin)],
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


# --- Cafeteria Order Item Endpoints ---
@app.post(
    "/menu-items/",
    response_model=CafeteriaOrderItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria menu item (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def create_cafeteria_order_item(
    item: CafeteriaOrderItem,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    created_item = await item_crud.create_item(item)
    return created_item


@app.get(
    "/menu-items/",
    response_model=List[CafeteriaOrderItem],
    summary="Get all cafeteria menu items (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_cafeteria_order_items(
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    items = await item_crud.get_all_items()
    return items


@app.get(
    "/menu-items/{item_id}",
    response_model=CafeteriaOrderItem,
    summary="Get a cafeteria menu item by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
)
async def get_cafeteria_order_item_by_id(
    item_id: str,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    item = await item_crud.get_item_by_id(item_id)
    if item:
        return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria menu item not found"
    )


@app.put(
    "/menu-items/{item_id}",
    response_model=CafeteriaOrderItem,
    summary="Update an existing cafeteria menu item (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def update_cafeteria_order_item(
    item_id: str,
    item: CafeteriaOrderItem,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    updated_item = await item_crud.update_item(item_id, item)
    if updated_item:
        return updated_item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria menu item not found"
    )


@app.delete(
    "/menu-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cafeteria menu item (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def delete_cafeteria_order_item(
    item_id: str,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    deleted = await item_crud.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafeteria menu item not found",
        )
    return


# --- Cafeteria Order Endpoints ---
@app.post(
    "/orders/",
    response_model=CafeteriaOrder,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria order (Authenticated User)",
)
async def create_cafeteria_order(
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
    current_user_id: str = Depends(get_current_user_id),  # Get user ID from token
):
    # Ensure the order is made by the authenticated user
    if str(order.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create orders for other users.",
        )
    created_order = await order_crud.create_order(order)
    return created_order


@app.get(
    "/orders/",
    response_model=List[CafeteriaOrder],
    summary="Get all cafeteria orders (Admin/Staff Only)",
    dependencies=[Depends(is_staff_or_admin)],
)
async def get_all_cafeteria_orders(
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    orders = await order_crud.get_all_orders()
    return orders


@app.get(
    "/orders/{order_id}",
    response_model=CafeteriaOrder,
    summary="Get a cafeteria order by ID (Admin/Staff or Self)",
)
async def get_cafeteria_order_by_id(
    order_id: str,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    order = await order_crud.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
        )

    # Admin/Staff can view any order, Guests can only view their own
    if (
        current_user_payload["role"] == UserRole.GUEST.value
        and str(order.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this order.",
        )

    return order


@app.put(
    "/orders/{order_id}",
    response_model=CafeteriaOrder,
    summary="Update an existing cafeteria order (Admin/Staff or Self)",
    dependencies=[Depends(JWTBearer())],
)
async def update_cafeteria_order(
    order_id: str,
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    current_order = await order_crud.get_order_by_id(order_id)
    if not current_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
        )

    # Admin/Staff can update any order, Guests can only update their own
    if (
        current_user_payload["role"] == UserRole.GUEST.value
        and str(current_order.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this order.",
        )

    # Specific logic for guests: e.g., can only cancel their own order
    if current_user_payload["role"] == UserRole.GUEST.value:
        if (
            "status" in order.model_dump(exclude_unset=True)
            and order.status != current_order.status
            and order.status != current_order.status.cancelled
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guests can only change order status to 'cancelled'.",
            )

    updated_order = await order_crud.update_order(order_id, order)
    if updated_order:
        return updated_order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
    )


@app.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cafeteria order (Admin/Staff Only)",
    dependencies=[Depends(is_staff_or_admin)],
)
async def delete_cafeteria_order(
    order_id: str, order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud)
):
    deleted = await order_crud.delete_order(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
        )
    return


# --- Boat Endpoints ---
@app.post(
    "/boats/",
    response_model=Boat,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def create_boat(boat: Boat, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    created_boat = await boat_crud.create_boat(boat)
    return created_boat


@app.get(
    "/boats/",
    response_model=List[Boat],
    summary="Get all boats (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_boats(boat_crud: BoatCRUD = Depends(get_boat_crud)):
    boats = await boat_crud.get_all_boats()
    return boats


@app.get(
    "/boats/{boat_id}",
    response_model=Boat,
    summary="Get a boat by ID (Any Authenticated User)",
    dependencies=[Depends(JWTBearer())],
)
async def get_boat_by_id(boat_id: str, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    boat = await boat_crud.get_boat_by_id(boat_id)
    if boat:
        return boat
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found")


@app.put(
    "/boats/{boat_id}",
    response_model=Boat,
    summary="Update an existing boat (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def update_boat(
    boat_id: str, boat: Boat, boat_crud: BoatCRUD = Depends(get_boat_crud)
):
    updated_boat = await boat_crud.update_boat(boat_id, boat)
    if updated_boat:
        return updated_boat
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found")


@app.delete(
    "/boats/{boat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a boat (Admin Only)",
    dependencies=[Depends(is_admin)],
)
async def delete_boat(boat_id: str, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    deleted = await boat_crud.delete_boat(boat_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found"
        )
    return


# --- Boat Booking Endpoints ---
@app.post(
    "/boat-bookings/",
    response_model=BoatBooking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat booking (Authenticated User)",
)
async def create_boat_booking(
    booking: BoatBooking,
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
    current_user_id: str = Depends(get_current_user_id),  # Get user ID from token
):
    # Ensure the booking is made by the authenticated user
    if str(booking.user_id) != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create bookings for other users.",
        )
    created_booking = await booking_crud.create_booking(booking)
    return created_booking


@app.get(
    "/boat-bookings/",
    response_model=List[BoatBooking],
    summary="Get all boat bookings (Admin/Staff Only)",
    dependencies=[Depends(is_staff_or_admin)],
)
async def get_all_boat_bookings(
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
):
    bookings = await booking_crud.get_all_bookings()
    return bookings


@app.get(
    "/boat-bookings/{booking_id}",
    response_model=BoatBooking,
    summary="Get a boat booking by ID (Admin/Staff or Self)",
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

    # Admin/Staff can view any booking, Guests can only view their own
    if (
        current_user_payload["role"] == UserRole.GUEST.value
        and str(booking.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this booking.",
        )

    return booking


@app.put(
    "/boat-bookings/{booking_id}",
    response_model=BoatBooking,
    summary="Update an existing boat booking (Admin/Staff or Self)",
    dependencies=[Depends(JWTBearer())],
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

    # Admin/Staff can update any booking, Guests can only update their own
    if (
        current_user_payload["role"] == UserRole.GUEST.value
        and str(current_booking.user_id) != current_user_payload["user_id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this booking.",
        )

    # Specific logic for guests: e.g., can only cancel their own booking
    if current_user_payload["role"] == UserRole.GUEST.value:
        allowed_fields = {
            "notes",
            "status",
        }  # Example: allow guests to update notes or cancel status

        update_data_keys = set(booking.model_dump(exclude_unset=True).keys())
        if not update_data_keys.issubset(allowed_fields):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guests can only update specific fields (notes, status).",
            )

        if (
            "status" in update_data_keys
            and booking.status != current_booking.status
            and booking.status != current_booking.status.cancelled
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


@app.delete(
    "/boat-bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a boat booking (Admin/Staff Only)",
    dependencies=[Depends(is_staff_or_admin)],
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
