from typing import Annotated, Dict, Any
from datetime import datetime, timedelta, timezone
import string

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from icecream import ic

from user_service import bootstrap
from user_service.config import SECRET_KEY
from user_service.domains import models
from user_service import views

bus = bootstrap.bootstrap()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    users = views.fetch_models_from_database(
        model_type=models.User, uow=bus.uow, id=user_id
    )

    if not users:
        raise credentials_exception
    return users[0]


async def get_current_unlock_user(
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)]
):
    if current_user["locked"]:
        raise HTTPException(status_code=400, detail="Account locked")
    return current_user
