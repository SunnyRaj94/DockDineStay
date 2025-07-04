from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from fastapi.encoders import jsonable_encoder

from dockdinestay.db import User, UpdateUser, UserCRUD, UserRole
from dockdinestay.db.utils import hash_password
from dockdinestay.auth.auth_bearer import JWTBearer
from dockdinestay.auth.auth_utils import (
    get_current_user_id,
    get_current_user_payload,
    is_admin,
)
from dockdinestay.routers.dependencies import get_user_crud

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Registration)",
)
async def create_user(user: User, user_crud: UserCRUD = Depends(get_user_crud)):
    user.password = hash_password(user.password)
    if not user.role:
        user.role = UserRole.CUSTOMER
    created_user = await user_crud.create_user(user)
    return created_user


@router.get(
    "/",
    response_model=List[User],
    summary="Get all users (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def get_all_users(user_crud: UserCRUD = Depends(get_user_crud)):
    users = await user_crud.get_all_users()
    return jsonable_encoder(users, by_alias=False)


@router.get(
    "/me", response_model=User, summary="Get current authenticated user's profile"
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


@router.get(
    "/{user_id}",
    response_model=User,
    summary="Get a user by ID (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def get_user_by_id(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    user = await user_crud.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.patch(
    "/{user_id}",
    response_model=User,
    summary="Update an existing user (Admin or Self)",
    dependencies=[Depends(JWTBearer())],
)
async def update_user(
    user_id: str,
    user_data_update: UpdateUser,
    user_crud: UserCRUD = Depends(get_user_crud),
    current_user_payload: dict = Depends(get_current_user_payload),
):
    if (
        current_user_payload["role"] != UserRole.ADMIN.value
        and current_user_payload["user_id"] != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user.",
        )

    if user_data_update.password:
        user_data_update.password = hash_password(user_data_update.password)

    updated_user = await user_crud.update_user(user_id, user_data_update)

    if updated_user:
        return updated_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found or no changes made.",
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (Admin Only)",
    dependencies=[Depends(JWTBearer()), Depends(is_admin)],
)
async def delete_user(user_id: str, user_crud: UserCRUD = Depends(get_user_crud)):
    deleted = await user_crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return
