from __future__ import annotations
from datetime import date, datetime
from typing import Optional
import uuid

from user_service.domains import events


class User:
    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        profile: Profile = None,
        locked: bool = False,
        id: str = str(uuid.uuid4()),
        created_time: datetime = datetime.utcnow(),
        updated_time: datetime = datetime.utcnow(),
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.profile = profile
        self.locked = locked
        self.created_time = created_time
        self.updated_time = updated_time
        self.events = []
        # self.profile = Profile()
        event = events.Registered(user_id=self.id)
        self.events.append(event)

    def __repr__(self):
        return f"<User {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)


class Profile:
    def __init__(
        self,
        user_id: str,
        backup_email: str = None,
        gender: str = None,
        date_of_birth: str = None,
        id: str = str(uuid.uuid4()),
    ):
        self.id = id
        self.user_id = user_id
        self.backup_email = backup_email
        self.gender = gender
        self.date_of_birth = date_of_birth
