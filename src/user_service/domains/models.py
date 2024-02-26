from __future__ import annotations
from datetime import date, datetime
import uuid

from user_service.domains import events


class BaseModel:
    def __init__(
        self,
    ):
        self.id = str(uuid.uuid4())
        self.created_time = datetime.utcnow()
        self.updated_time = datetime.utcnow()


class User(BaseModel):
    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        profile: Profile = None,
        locked: bool = False,
    ):
        super().__init__()
        self.username = username
        self.email = email
        self.password = password
        self.profile = profile
        self.locked = locked
        self.events = []
        # self.profile = Profile()
        # event = events.Registered(user_id=self.id)
        # self.events.append(event)

    def __repr__(self):
        return f"<User {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)


class Profile(BaseModel):
    def __init__(
        self,
        user_id: str,
        backup_email: str = None,
        gender: str = None,
        date_of_birth: date = None,
    ):
        super().__init__()
        self.user_id = user_id
        self.backup_email = backup_email
        self.gender = gender
        self.date_of_birth = date_of_birth
