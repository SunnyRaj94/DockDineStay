from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

# Import your routers
from dockdinestay.routers import (
    auth,
    users,
    hotel_rooms,
    hotel_bookings,
    cafeteria_tables,
    cafeteria_menu,
    cafeteria_orders,
    boats,
    boat_bookings,
)


app = FastAPI(
    title="DockDineStay API",
    description="API for managing hotel rooms, bookings, cafeteria services, and boat rentals.",
    version="0.1.0",
    json_encoders={ObjectId: str},
    openapi_extra={
        "components": {
            "schemas": {
                "User": {"properties": {"id": {"type": "string", "format": "objectid"}}}
            }
        }
    },
)
print("Attempting to add CORS middleware with allow_origins=['*']")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMPORARY: For testing purposes ONLY
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)


# Updated CORS configuration
# origins = [
#     "http://localhost",
#     "http://localhost:5173",
#     "http://127.0.0.1",
#     "http://127.0.0.1:5173",
#     "https://your-production-frontend.com",  # Add when you deploy frontend
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"],  # Important for custom headers
# )


# --- Root Endpoint ---
@app.get("/", summary="Root endpoint")
async def read_root():
    return {"message": "Welcome to DockDineStay API!"}


# --- Include Routers ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hotel_rooms.router)
app.include_router(hotel_bookings.router)
app.include_router(cafeteria_tables.router)
app.include_router(cafeteria_menu.router)
app.include_router(cafeteria_orders.router)
app.include_router(boats.router)
app.include_router(boat_bookings.router)
