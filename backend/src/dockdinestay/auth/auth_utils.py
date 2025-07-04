# backend/auth/auth_utils.py

from fastapi import Depends, HTTPException, status, Request
from typing import List, Union

from dockdinestay.db.utils import UserRole  # Import your UserRole enum
from dockdinestay.auth.auth_bearer import (
    JWTBearer,
)  # We need JWTBearer to get the payload


# Dependency to get the current user's payload from the token
# This depends on JWTBearer being executed first, which stores the payload in request.state
def get_current_user_payload(request: Request = Depends(JWTBearer())) -> dict:
    """
    Retrieves the decoded user payload from the request state,
    which was set by the JWTBearer dependency.
    """
    payload = request.state.user_payload
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Payload missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_user_id(payload: dict = Depends(get_current_user_payload)) -> str:
    """Retrieves the user_id from the current user's JWT payload."""
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: User ID missing in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_current_user_role(
    payload: dict = Depends(get_current_user_payload),
) -> UserRole:
    """Retrieves the role from the current user's JWT payload."""
    role_str = payload.get("role")
    if not role_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: User role missing in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return UserRole(role_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Invalid user role in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Role-Based Authorization Dependencies ---


def has_role(required_roles: Union[UserRole, List[UserRole]]):
    """
    A factory function that creates a dependency to check if the current user
    has any of the required roles.
    """
    if not isinstance(required_roles, list):
        required_roles = [required_roles]

    async def _has_role(current_user_role: UserRole = Depends(get_current_user_role)):
        if current_user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required roles: {[role.value for role in required_roles]}",
            )
        return current_user_role

    return _has_role


# Specific role dependencies (using the factory for convenience)
is_admin = has_role(UserRole.ADMIN)
is_staff_or_admin = has_role([UserRole.BACK_DESK, UserRole.ADMIN])
is_guest_or_staff_or_admin = has_role(
    [UserRole.BACK_DESK, UserRole.FRONT_DESK, UserRole.ADMIN]
)
# You can add more specific ones as needed, e.g., is_guest
