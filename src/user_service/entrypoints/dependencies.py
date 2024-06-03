from datetime import datetime, timedelta, timezone
import string
import jwt
from user_service.config import SECRET_KEY
from user_service import bootstrap

bus = bootstrap.bootstrap()


class InvalidPassword(Exception):
    pass


def validate_password(password: str):
    # Minimum length
    if len(password) < 8:
        raise InvalidPassword("Invalid password")

    # No spaces
    if " " in password:
        raise InvalidPassword("Invalid password")

    # At least one digit
    if not any(c.isdigit() for c in password):
        raise InvalidPassword("Invalid password")

    # At least one special character
    if not any(c in string.punctuation for c in password):
        raise InvalidPassword("Invalid password")

    return True


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
