# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from dockdinestay.db import UserCRUD
from dockdinestay.db.utils import verify_password
from dockdinestay.auth.auth_handler import create_access_token
from dockdinestay.auth.token import Token
from dockdinestay.routers.dependencies import get_user_crud

router = APIRouter(
    tags=["Authentication"],
)


@router.post(
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

    access_token_data = {
        "sub": user_in_db.username,
        "user_id": str(user_in_db.id),
        "role": user_in_db.role.value,  # Correctly access the enum value
    }

    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}
