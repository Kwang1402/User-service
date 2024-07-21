from __future__ import annotations
from datetime import date, datetime
import dataclasses
import uuid


@dataclasses.dataclass
class BaseModel:
    def __init__(
        self,
        message_id: str,
    ):
        self.id = str(uuid.uuid4())
        self.created_time = datetime.now()
        self.updated_time = datetime.now()
        self.message_id = message_id
        self.events = []

    _datetime_format: str = "%Y-%m-%d %H:%M:%S"

    @property
    def json(self):
        """json."""
        data = {
            key: val for key, val in self.__dict__.items() if not key.startswith("_")
        }
        for attr, value in data.items():
            if isinstance(value, datetime):
                data[attr] = value.strftime(self._datetime_format)
            if isinstance(value, set):
                data[attr] = list(value)
        return data


class User(BaseModel):
    def __init__(
        self,
        message_id: str,
        username: str,
        email: str,
        password: str,
        secret_token: str,
        two_factor_auth_enabled: bool = False,
        locked: bool = False,
    ):
        super().__init__(message_id)
        self.username = username
        self.email = email
        self.password = password
        self.secret_token = secret_token
        self.two_factor_auth_enabled = two_factor_auth_enabled
        self.locked = locked

    def __repr__(self):
        return f"<User {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def enable_two_factor_auth(self):
        self.two_factor_auth_enabled = True

    def change_password(self, password):
        self.password = password


class Profile(BaseModel):
    def __init__(
        self,
        message_id: str,
        user_id: str,
        first_name: str = None,
        last_name: str = None,
        backup_email: str = None,
        gender: str = None,
        date_of_birth: date = None,
    ):
        super().__init__(message_id)
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.backup_email = backup_email
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.friends = 0
        self.followers = 0

    def __repr__(self):
        return f"<Profile {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)


class FriendRequest(BaseModel):
    def __init__(
        self,
        message_id: str,
        sender_id: str,
        receiver_id: str,
    ):
        super().__init__(message_id)
        self.sender_id = sender_id
        self.receiver_id = receiver_id

    def __repr__(self):
        return f"<FriendRequest {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, FriendRequest):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)


class Friend(BaseModel):
    def __init__(
        self,
        message_id: str,
        sender_id: str,
        receiver_id: str,
    ):
        super().__init__(message_id)
        self.sender_id = sender_id
        self.receiver_id = receiver_id

    def __repr__(self):
        return f"<Friend {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, Friend):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
