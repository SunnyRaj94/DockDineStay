from fastapi import FastAPI, HTTPException, status, Depends
from typing import List
from fastapi.security import OAuth2PasswordRequestForm

from dockdinestay.db import (
    User,
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


# --- NEW: Authentication Endpoints ---
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
    if not verify_password(form_data.password, user_in_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token payload with subject (username), user_id, and role
    access_token_data = {
        "sub": user_in_db.username,
        "user_id": str(user_in_db.id),  # Convert ObjectId to string
        "role": user_in_db.role.value,  # Get string value of enum
    }

    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}


# --- User Endpoints (MODIFIED for password hashing and protection) ---
@app.post(
    "/users/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(user: User, user_crud: UserCRUD = Depends(get_user_crud)):
    # Hash the password before creating the user
    user.password = hash_password(user.password)
    created_user = await user_crud.create_user(user)
    return created_user


# Protecting all GET operations for now as a basic step
@app.get(
    "/users/",
    response_model=List[User],
    summary="Get all users",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_users(user_crud: UserCRUD = Depends(get_user_crud)):
    users = await user_crud.get_all_users()
    return users


@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="Get a user by ID",
    dependencies=[Depends(JWTBearer())],
)
async def get_user_by_id(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    user = await user_crud.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.put(
    "/users/{user_id}",
    response_model=User,
    summary="Update an existing user",
    dependencies=[Depends(JWTBearer())],
)
async def update_user(
    user_id: str, user: User, user_crud: UserCRUD = Depends(get_user_crud)
):
    # If password is being updated, hash it
    if user.password:
        user.password = hash_password(user.password)
    updated_user = await user_crud.update_user(user_id, user)
    if updated_user:
        return updated_user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    dependencies=[Depends(JWTBearer())],
)
async def delete_user(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    deleted = await user_crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return


# --- Hotel Room Endpoints (Protecting all for now) ---
@app.post(
    "/rooms/",
    response_model=HotelRoom,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel room",
    dependencies=[Depends(JWTBearer())],
)
async def create_hotel_room(
    room: HotelRoom, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    created_room = await room_crud.create_room(room)
    return created_room


@app.get(
    "/rooms/",
    response_model=List[HotelRoom],
    summary="Get all hotel rooms",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_hotel_rooms(room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)):
    rooms = await room_crud.get_all_rooms()
    return rooms


@app.get(
    "/rooms/{room_id}",
    response_model=HotelRoom,
    summary="Get a hotel room by ID",
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
    summary="Update an existing hotel room",
    dependencies=[Depends(JWTBearer())],
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
    summary="Delete a hotel room",
    dependencies=[Depends(JWTBearer())],
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


# --- Hotel Booking Endpoints (Protecting all for now) ---
@app.post(
    "/bookings/",
    response_model=HotelBooking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel booking",
    dependencies=[Depends(JWTBearer())],
)
async def create_hotel_booking(
    booking: HotelBooking,
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
):
    created_booking = await booking_crud.create_booking(booking)
    return created_booking


@app.get(
    "/bookings/",
    response_model=List[HotelBooking],
    summary="Get all hotel bookings",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_hotel_bookings(
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
):
    bookings = await booking_crud.get_all_bookings()
    return bookings


@app.get(
    "/bookings/{booking_id}",
    response_model=HotelBooking,
    summary="Get a hotel booking by ID",
    dependencies=[Depends(JWTBearer())],
)
async def get_hotel_booking_by_id(
    booking_id: str, booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud)
):
    booking = await booking_crud.get_booking_by_id(booking_id)
    if booking:
        return booking
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Hotel booking not found"
    )


@app.put(
    "/bookings/{booking_id}",
    response_model=HotelBooking,
    summary="Update an existing hotel booking",
    dependencies=[Depends(JWTBearer())],
)
async def update_hotel_booking(
    booking_id: str,
    booking: HotelBooking,
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
):
    updated_booking = await booking_crud.update_booking(booking_id, booking)
    if updated_booking:
        return updated_booking
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Hotel booking not found"
    )


@app.delete(
    "/bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hotel booking",
    dependencies=[Depends(JWTBearer())],
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


# --- Cafeteria Table Endpoints (Protecting all for now) ---
@app.post(
    "/tables/",
    response_model=CafeteriaTable,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria table",
    dependencies=[Depends(JWTBearer())],
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
    summary="Get all cafeteria tables",
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
    summary="Get a cafeteria table by ID",
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
    summary="Update an existing cafeteria table",
    dependencies=[Depends(JWTBearer())],
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
    summary="Delete a cafeteria table",
    dependencies=[Depends(JWTBearer())],
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


# --- Cafeteria Order Item Endpoints (Protecting all for now) ---
@app.post(
    "/menu-items/",
    response_model=CafeteriaOrderItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria menu item",
    dependencies=[Depends(JWTBearer())],
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
    summary="Get all cafeteria menu items",
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
    summary="Get a cafeteria menu item by ID",
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
    summary="Update an existing cafeteria menu item",
    dependencies=[Depends(JWTBearer())],
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
    summary="Delete a cafeteria menu item",
    dependencies=[Depends(JWTBearer())],
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


# --- Cafeteria Order Endpoints (Protecting all for now) ---
@app.post(
    "/orders/",
    response_model=CafeteriaOrder,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria order",
    dependencies=[Depends(JWTBearer())],
)
async def create_cafeteria_order(
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    created_order = await order_crud.create_order(order)
    return created_order


@app.get(
    "/orders/",
    response_model=List[CafeteriaOrder],
    summary="Get all cafeteria orders",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_cafeteria_orders(
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    orders = await order_crud.get_all_orders()
    return orders


@app.get(
    "/orders/{order_id}",
    response_model=CafeteriaOrder,
    summary="Get a cafeteria order by ID",
    dependencies=[Depends(JWTBearer())],
)
async def get_cafeteria_order_by_id(
    order_id: str, order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud)
):
    order = await order_crud.get_order_by_id(order_id)
    if order:
        return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
    )


@app.put(
    "/orders/{order_id}",
    response_model=CafeteriaOrder,
    summary="Update an existing cafeteria order",
    dependencies=[Depends(JWTBearer())],
)
async def update_cafeteria_order(
    order_id: str,
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    updated_order = await order_crud.update_order(order_id, order)
    if updated_order:
        return updated_order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
    )


@app.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cafeteria order",
    dependencies=[Depends(JWTBearer())],
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


# --- Boat Endpoints (Protecting all for now) ---
@app.post(
    "/boats/",
    response_model=Boat,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat",
    dependencies=[Depends(JWTBearer())],
)
async def create_boat(boat: Boat, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    created_boat = await boat_crud.create_boat(boat)
    return created_boat


@app.get(
    "/boats/",
    response_model=List[Boat],
    summary="Get all boats",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_boats(boat_crud: BoatCRUD = Depends(get_boat_crud)):
    boats = await boat_crud.get_all_boats()
    return boats


@app.get(
    "/boats/{boat_id}",
    response_model=Boat,
    summary="Get a boat by ID",
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
    summary="Update an existing boat",
    dependencies=[Depends(JWTBearer())],
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
    summary="Delete a boat",
    dependencies=[Depends(JWTBearer())],
)
async def delete_boat(boat_id: str, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    deleted = await boat_crud.delete_boat(boat_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found"
        )
    return


# --- Boat Booking Endpoints (Protecting all for now) ---
@app.post(
    "/boat-bookings/",
    response_model=BoatBooking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat booking",
    dependencies=[Depends(JWTBearer())],
)
async def create_boat_booking(
    booking: BoatBooking, booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud)
):
    created_booking = await booking_crud.create_booking(booking)
    return created_booking


@app.get(
    "/boat-bookings/",
    response_model=List[BoatBooking],
    summary="Get all boat bookings",
    dependencies=[Depends(JWTBearer())],
)
async def get_all_boat_bookings(
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
):
    bookings = await booking_crud.get_all_bookings()
    return bookings


@app.get(
    "/boat-bookings/{booking_id}",
    response_model=BoatBooking,
    summary="Get a boat booking by ID",
    dependencies=[Depends(JWTBearer())],
)
async def get_boat_booking_by_id(
    booking_id: str, booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud)
):
    booking = await booking_crud.get_booking_by_id(booking_id)
    if booking:
        return booking
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Boat booking not found"
    )


@app.put(
    "/boat-bookings/{booking_id}",
    response_model=BoatBooking,
    summary="Update an existing boat booking",
    dependencies=[Depends(JWTBearer())],
)
async def update_boat_booking(
    booking_id: str,
    booking: BoatBooking,
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
):
    updated_booking = await booking_crud.update_booking(booking_id, booking)
    if updated_booking:
        return updated_booking
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Boat booking not found"
    )


@app.delete(
    "/boat-bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a boat booking",
    dependencies=[Depends(JWTBearer())],
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
