import dataclasses
from datetime import date


class Event:
    pass


@dataclasses.dataclass
class Registered(Event):
    user_id: str
    backup_email: str
    gender: str
    date_of_birth: date


@dataclasses.dataclass
class ResetPassword(Event):
    user_id: str
    new_password: str
