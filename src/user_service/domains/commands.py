import dataclasses
from datetime import date


class Command:
    pass


@dataclasses.dataclass
class RegisterCommand(Command):
    username: str
    email: str
    password: str
    backup_email: str
    gender: str
    date_of_birth: date
