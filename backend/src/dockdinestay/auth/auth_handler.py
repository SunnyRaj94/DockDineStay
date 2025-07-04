from datetime import datetime, timedelta, timezone   # Import timezone
from typing import Optional

from jose import jwt, JWTError

from fastapi import HTTPException, status

from dockdinestay.configs import env

SECRET_KEY = env.get(
    "SECRET_KEY", "your-super-secret-key-that-should-be-strong-and-random"
)
ALGORITHM = "HS256"  # HMAC-SHA256 algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for access token validity


# --- JWT Token Functions ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new JWT access token.
    'data' should contain payload like {"sub": "username"}.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodes a JWT token and returns the payload.
    Raises HTTPException if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token decoding error: {str(e)}",
        )
