from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from utils.exceptions import InvalidTokenError


SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def create_access_token(data: dict) -> str:
    payload_to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload_to_encode["exp"] = expire
    encoded_jwt = jwt.encode(payload_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email = payload.get("sub")
        if not email:
            raise InvalidTokenError("Missing 'sub' in token")
        return email
    except JWTError as e:
        raise InvalidTokenError(str(e)) from e


