from typing import Optional
from datetime import date

from user_service.domains import Message


class Event(Message):
    pass


class RegisteredEvent(Event):
    user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    backup_email: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[date]


class AcceptedFriendRequestEvent(Event):
    friend_request_id: str
