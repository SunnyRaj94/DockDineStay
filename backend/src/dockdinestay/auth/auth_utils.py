from fastapi import Depends, HTTPException, status, Request
from typing import List, Union

from dockdinestay.db.utils import UserRole  # Import your UserRole enum
from dockdinestay.auth.auth_bearer import (
    JWTBearer,
)  # We need JWTBearer to get the payload


def get_current_user_payload(
    request: Request,
    # <-- CRUCIAL: JWTBearer() MUST be a dependency here!
    # It extracts and validates the token, and sets request.state.user_payload
    token_data: str = Depends(JWTBearer()),
) -> dict:
    """
    Retrieves the decoded user payload from the request state,
    which was set by the JWTBearer dependency.
    """
    # Now, request.state.user_payload should be populated by JWTBearer
    payload = request.state.user_payload
    if not payload:
        # This check might be redundant if JWTBearer ensures payload is set or raises
        # but it's harmless to keep as a safeguard.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Payload missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


# And your get_current_user_id (if it depends on get_current_user_payload)
def get_current_user_id(
    payload: dict = Depends(get_current_user_payload),  # This is correct
) -> str:
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: User ID missing from payload.",
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

    # The _has_role function itself doesn't need JWTBearer directly,
    # it relies on get_current_user_role which in turn relies on get_current_user_payload.
    # The JWTBearer dependency must be applied at the route level for these to work.
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
