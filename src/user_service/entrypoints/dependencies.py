import string
import jwt
from user_service.config import SECRET_KEY
from user_service import bootstrap

bus = bootstrap.bootstrap()


class InvalidPassword(Exception):
    pass


class UnauthorizedAccess(Exception):
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


def validate_token(token, user_id):
    if not token:
        raise UnauthorizedAccess("Authorization token missing")

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        authenticated_user_id = decoded_token.get("user_id")

        if authenticated_user_id != user_id:
            raise UnauthorizedAccess("Unauthorized access to user account")

    except jwt.InvalidTokenError:
        raise UnauthorizedAccess("Invalid token")
