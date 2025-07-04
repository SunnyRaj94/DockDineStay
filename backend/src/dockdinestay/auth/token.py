from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Pydantic model for the JWT token response."""

    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class TokenData(BaseModel):
    """Pydantic model for the data expected in a JWT token."""

    username: Optional[str] = None
    # Add other fields like user_id, role if you put them in the token payload
    user_id: Optional[str] = None
    role: Optional[str] = None
