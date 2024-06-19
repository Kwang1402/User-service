from datetime import date
from user_service.domains import Message


class Event(Message):
    pass


class RegisteredEvent(Event):
    user_id: str
    first_name: str | None = None
    last_name: str | None = None
    backup_email: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None


class AcceptedFriendRequestEvent(Event):
    sender_id: str
    receiver_id: str
