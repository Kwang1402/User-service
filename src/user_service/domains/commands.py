from dataclasses import dataclass
from datetime import datetime


class Command:
    pass


@dataclass
# class RegisterCommand(Command):
class Register(Command):
    username: str
    email: str
    password: str
    backup_email: str
    gender: str
    date_of_birth: datetime
