from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dockdinestay.auth.auth_handler import (
    decode_token,
)  # Import your decode_token function


class JWTBearer(HTTPBearer):
    """
    A custom security scheme that extracts and validates a JWT token
    from the Authorization header.
    """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme. Must be Bearer.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Decode the token using your auth_handler function
            payload = decode_token(credentials.credentials)

            # You can store the payload (e.g., user_id, role) in the request state
            # for later use in route functions if needed.
            request.state.user_payload = payload

            return payload  # Return the decoded payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated. Missing Bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
