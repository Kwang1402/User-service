from dataclasses import dataclass
from datetime import date, datetime
import uuid
import string


class Profile:
    def __init__(
        self,
        id: str,
        user_id: str,
        backup_email: str,
        gender: str,
        date_of_birth: date,
    ):
        self.id = id
        self.user_id = user_id
        self.backup_email = backup_email
        self.gender = gender
        self.date_of_birth = date_of_birth


class User:
    def __init__(
        self,
        id: str(uuid.uuid4()),
        username: str,
        password: str,
        locked: bool = False,
        created_time: datetime = None,
        updated_time: datetime = None,
    ):
        self.id = id
        self.username = username
        self.password = password
        self.locked = locked
        self.created_time = created_time
        self.updated_time = updated_time


class EventType:
    def __init__(
        self,
        id: int,
        type: str,
    ):
        self.id = id
        self.type = type


class Event:
    def __init__(
        self,
        id: str,
        type_id: int,
        created_by: str,
    ):
        self.id = id
        self.type_id = type_id
        self.created_by = created_by


class TrustedDevice:
    def __init__(
        self,
        id: str,
        user_id: str,
    ):
        self.id = id
        self.user_id = user_id


def validate_password(password: str) -> bool:
    # Minimum length
    if len(password) < 8:
        return False

    # No spaces
    if " " in password:
        return False

    # At least one digit
    if not any(c.isdigit() for c in password):
        return False

    # At least one special character
    if not any(c in string.punctuation for c in password):
        return False

    return True
