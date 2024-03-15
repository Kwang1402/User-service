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


@dataclasses.dataclass
class LoginCommand(Command):
    email: str
    password: str


@dataclasses.dataclass
class GetUserCommand(Command):
    user_id: str
    token: str


@dataclasses.dataclass
class ResetPasswordCommand(Command):
    email: str
    username: str
