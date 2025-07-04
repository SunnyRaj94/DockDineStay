from fastapi import FastAPI, HTTPException, status, Depends
from typing import List

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

app = FastAPI(
    title="DockDineStay API",
    description="API for managing hotel rooms, bookings, cafeteria services, and boat rentals.",
    version="0.1.0",
)


# --- Dependency to get a UserCRUD instance ---
# This function will be called by FastAPI's Depends()
# It creates a UserCRUD instance, passing the 'db' object to it.
def get_user_crud(database=Depends(lambda: db)) -> UserCRUD:
    """
    Dependency that provides a UserCRUD instance.
    """
    return UserCRUD(database)


def get_hotel_room_crud(
    database=Depends(lambda: db),
) -> HotelRoomCRUD:  # New dependency
    return HotelRoomCRUD(database)


def get_hotel_booking_crud(
    database=Depends(lambda: db),
) -> HotelBookingCRUD:  # New dependency
    return HotelBookingCRUD(database)


def get_cafeteria_table_crud(
    database=Depends(lambda: db),
) -> CafeteriaTableCRUD:  # New dependency
    return CafeteriaTableCRUD(database)


def get_cafeteria_order_item_crud(
    database=Depends(lambda: db),
) -> CafeteriaOrderItemCRUD:  # New dependency
    return CafeteriaOrderItemCRUD(database)


def get_cafeteria_order_crud(
    database=Depends(lambda: db),
) -> CafeteriaOrderCRUD:  # New dependency
    return CafeteriaOrderCRUD(database)


def get_boat_crud(database=Depends(lambda: db)) -> BoatCRUD:  # New dependency
    return BoatCRUD(database)


def get_boat_booking_crud(
    database=Depends(lambda: db),
) -> BoatBookingCRUD:  # New dependency
    return BoatBookingCRUD(database)


# --- API Endpoints for Users ---


@app.get("/", summary="Root endpoint")
async def read_root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to DockDineStay API!"}


@app.post(
    "/users/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(user: User, user_crud: UserCRUD = Depends(get_user_crud)):
    """
    Create a new user in the database.
    The password will be hashed before storage.
    """
    created_user = await user_crud.create_user(user)
    return created_user


@app.get("/users/", response_model=List[User], summary="Get all users")
async def get_all_users(user_crud: UserCRUD = Depends(get_user_crud)):
    """
    Retrieve a list of all users from the database.
    """
    users = await user_crud.get_all_users()
    return users


@app.get("/users/{user_id}", response_model=User, summary="Get a user by ID")
async def get_user_by_id(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    """
    Retrieve a single user by their ID.
    """
    user = await user_crud.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.put("/users/{user_id}", response_model=User, summary="Update an existing user")
async def update_user(
    user_id: str, user: User, user_crud: UserCRUD = Depends(get_user_crud)
):
    """
    Update an existing user's information.
    The password will be hashed if updated.
    """
    updated_user = await user_crud.update_user(user_id, user)
    if updated_user:
        return updated_user
    # The CRUD method itself raises 304 if no modification, so we only need to handle 404 here
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.delete(
    "/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user"
)
async def delete_user(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    """
    Delete a user from the database by their ID.
    """
    deleted = await user_crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "User Deleted"}


# --- Hotel Room Endpoints (NEW) ---
@app.post(
    "/rooms/",
    response_model=HotelRoom,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel room",
)
async def create_hotel_room(
    room: HotelRoom, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    """
    Create a new hotel room.
    """
    created_room = await room_crud.create_room(room)
    return created_room


@app.get("/rooms/", response_model=List[HotelRoom], summary="Get all hotel rooms")
async def get_all_hotel_rooms(room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)):
    """
    Retrieve a list of all hotel rooms.
    """
    rooms = await room_crud.get_all_rooms()
    return rooms


@app.get("/rooms/{room_id}", response_model=HotelRoom, summary="Get a hotel room by ID")
async def get_hotel_room_by_id(
    room_id: str, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    """
    Retrieve a single hotel room by its ID.
    """
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
)
async def update_hotel_room(
    room_id: str,
    room: HotelRoom,
    room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud),
):
    """
    Update an existing hotel room's information.
    """
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
)
async def delete_hotel_room(
    room_id: str, room_crud: HotelRoomCRUD = Depends(get_hotel_room_crud)
):
    """
    Delete a hotel room from the database by its ID.
    """
    deleted = await room_crud.delete_room(room_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel room not found"
        )
    return


# --- Hotel Booking Endpoints (NEW) ---
@app.post(
    "/bookings/",
    response_model=HotelBooking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel booking",
)
async def create_hotel_booking(
    booking: HotelBooking,
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
):
    """
    Create a new hotel booking.
    Requires existing user_id and room_id. Checks room availability for dates.
    """
    created_booking = await booking_crud.create_booking(booking)
    return created_booking


@app.get(
    "/bookings/", response_model=List[HotelBooking], summary="Get all hotel bookings"
)
async def get_all_hotel_bookings(
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
):
    """
    Retrieve a list of all hotel bookings.
    """
    bookings = await booking_crud.get_all_bookings()
    return bookings


@app.get(
    "/bookings/{booking_id}",
    response_model=HotelBooking,
    summary="Get a hotel booking by ID",
)
async def get_hotel_booking_by_id(
    booking_id: str, booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud)
):
    """
    Retrieve a single hotel booking by its ID.
    """
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
)
async def update_hotel_booking(
    booking_id: str,
    booking: HotelBooking,
    booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud),
):
    """
    Update an existing hotel booking's information.
    """
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
)
async def delete_hotel_booking(
    booking_id: str, booking_crud: HotelBookingCRUD = Depends(get_hotel_booking_crud)
):
    """
    Delete a hotel booking from the database by its ID.
    """
    deleted = await booking_crud.delete_booking(booking_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel booking not found"
        )
    return


# --- Cafeteria Table Endpoints (NEW) ---
@app.post(
    "/tables/",
    response_model=CafeteriaTable,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria table",
)
async def create_cafeteria_table(
    table: CafeteriaTable,
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    """
    Create a new cafeteria table.
    """
    created_table = await table_crud.create_table(table)
    return created_table


@app.get(
    "/tables/", response_model=List[CafeteriaTable], summary="Get all cafeteria tables"
)
async def get_all_cafeteria_tables(
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    """
    Retrieve a list of all cafeteria tables.
    """
    tables = await table_crud.get_all_tables()
    return tables


@app.get(
    "/tables/{table_id}",
    response_model=CafeteriaTable,
    summary="Get a cafeteria table by ID",
)
async def get_cafeteria_table_by_id(
    table_id: str, table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud)
):
    """
    Retrieve a single cafeteria table by its ID.
    """
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
)
async def update_cafeteria_table(
    table_id: str,
    table: CafeteriaTable,
    table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud),
):
    """
    Update an existing cafeteria table's information.
    """
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
)
async def delete_cafeteria_table(
    table_id: str, table_crud: CafeteriaTableCRUD = Depends(get_cafeteria_table_crud)
):
    """
    Delete a cafeteria table from the database by its ID.
    """
    deleted = await table_crud.delete_table(table_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria table not found"
        )
    return


# --- Cafeteria Order Item Endpoints (NEW) ---
@app.post(
    "/menu-items/",
    response_model=CafeteriaOrderItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria menu item",
)
async def create_cafeteria_order_item(
    item: CafeteriaOrderItem,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    """
    Create a new cafeteria menu item (e.g., a dish or beverage).
    """
    created_item = await item_crud.create_item(item)
    return created_item


@app.get(
    "/menu-items/",
    response_model=List[CafeteriaOrderItem],
    summary="Get all cafeteria menu items",
)
async def get_all_cafeteria_order_items(
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    """
    Retrieve a list of all cafeteria menu items.
    """
    items = await item_crud.get_all_items()
    return items


@app.get(
    "/menu-items/{item_id}",
    response_model=CafeteriaOrderItem,
    summary="Get a cafeteria menu item by ID",
)
async def get_cafeteria_order_item_by_id(
    item_id: str,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    """
    Retrieve a single cafeteria menu item by its ID.
    """
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
)
async def update_cafeteria_order_item(
    item_id: str,
    item: CafeteriaOrderItem,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    """
    Update an existing cafeteria menu item's information.
    """
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
)
async def delete_cafeteria_order_item(
    item_id: str,
    item_crud: CafeteriaOrderItemCRUD = Depends(get_cafeteria_order_item_crud),
):
    """
    Delete a cafeteria menu item from the database by its ID.
    """
    deleted = await item_crud.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafeteria menu item not found",
        )
    return


# --- Cafeteria Order Endpoints (NEW) ---
@app.post(
    "/orders/",
    response_model=CafeteriaOrder,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cafeteria order",
)
async def create_cafeteria_order(
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    """
    Create a new cafeteria order for a user and table, including specific menu items.
    The `total_amount` will be calculated by the backend based on item prices.
    """
    created_order = await order_crud.create_order(order)
    return created_order


@app.get(
    "/orders/", response_model=List[CafeteriaOrder], summary="Get all cafeteria orders"
)
async def get_all_cafeteria_orders(
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    """
    Retrieve a list of all cafeteria orders.
    """
    orders = await order_crud.get_all_orders()
    return orders


@app.get(
    "/orders/{order_id}",
    response_model=CafeteriaOrder,
    summary="Get a cafeteria order by ID",
)
async def get_cafeteria_order_by_id(
    order_id: str, order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud)
):
    """
    Retrieve a single cafeteria order by its ID.
    """
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
)
async def update_cafeteria_order(
    order_id: str,
    order: CafeteriaOrder,
    order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud),
):
    """
    Update an existing cafeteria order's information.
    Note: User ID and Order Time cannot be changed.
    """
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
)
async def delete_cafeteria_order(
    order_id: str, order_crud: CafeteriaOrderCRUD = Depends(get_cafeteria_order_crud)
):
    """
    Delete a cafeteria order from the database by its ID.
    """
    deleted = await order_crud.delete_order(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cafeteria order not found"
        )
    return


# --- Boat Endpoints (NEW) ---
@app.post(
    "/boats/",
    response_model=Boat,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat",
)
async def create_boat(boat: Boat, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    """
    Create a new boat available for rental.
    """
    created_boat = await boat_crud.create_boat(boat)
    return created_boat


@app.get("/boats/", response_model=List[Boat], summary="Get all boats")
async def get_all_boats(boat_crud: BoatCRUD = Depends(get_boat_crud)):
    """
    Retrieve a list of all boats.
    """
    boats = await boat_crud.get_all_boats()
    return boats


@app.get("/boats/{boat_id}", response_model=Boat, summary="Get a boat by ID")
async def get_boat_by_id(boat_id: str, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    """
    Retrieve a single boat by its ID.
    """
    boat = await boat_crud.get_boat_by_id(boat_id)
    if boat:
        return boat
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found")


@app.put("/boats/{boat_id}", response_model=Boat, summary="Update an existing boat")
async def update_boat(
    boat_id: str, boat: Boat, boat_crud: BoatCRUD = Depends(get_boat_crud)
):
    """
    Update an existing boat's information.
    """
    updated_boat = await boat_crud.update_boat(boat_id, boat)
    if updated_boat:
        return updated_boat
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found")


@app.delete(
    "/boats/{boat_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a boat"
)
async def delete_boat(boat_id: str, boat_crud: BoatCRUD = Depends(get_boat_crud)):
    """
    Delete a boat from the database by its ID.
    """
    deleted = await boat_crud.delete_boat(boat_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat not found"
        )
    return


# --- Boat Booking Endpoints (NEW) ---
@app.post(
    "/boat-bookings/",
    response_model=BoatBooking,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new boat booking",
)
async def create_boat_booking(
    booking: BoatBooking, booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud)
):
    """
    Create a new boat rental booking for a user and a specific boat.
    Checks for boat availability and calculates total price based on hourly rate.
    """
    created_booking = await booking_crud.create_booking(booking)
    return created_booking


@app.get(
    "/boat-bookings/", response_model=List[BoatBooking], summary="Get all boat bookings"
)
async def get_all_boat_bookings(
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
):
    """
    Retrieve a list of all boat bookings.
    """
    bookings = await booking_crud.get_all_bookings()
    return bookings


@app.get(
    "/boat-bookings/{booking_id}",
    response_model=BoatBooking,
    summary="Get a boat booking by ID",
)
async def get_boat_booking_by_id(
    booking_id: str, booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud)
):
    """
    Retrieve a single boat booking by its ID.
    """
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
)
async def update_boat_booking(
    booking_id: str,
    booking: BoatBooking,
    booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud),
):
    """
    Update an existing boat booking's information.
    Re-validates time slots and recalculates price if dates change.
    """
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
)
async def delete_boat_booking(
    booking_id: str, booking_crud: BoatBookingCRUD = Depends(get_boat_booking_crud)
):
    """
    Delete a boat booking from the database by its ID.
    """
    deleted = await booking_crud.delete_booking(booking_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Boat booking not found"
        )
    return
