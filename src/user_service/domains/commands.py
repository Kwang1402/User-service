import dataclasses
from datetime import date


class Command:
    pass


@dataclasses.dataclass
class RegisterCommand(Command):
    username: str
    email: str
    password: str
    backup_email: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None


@dataclasses.dataclass
class EnableTwoFactorAuthCommand(Command):
    user_id: str


@dataclasses.dataclass
class VerifyEnableTwoFactorAuthCommand(Command):
    user_id: str
    otp_code: str


@dataclasses.dataclass
class LoginCommand(Command):
    email: str
    password: str


@dataclasses.dataclass
class GetUserCommand(Command):
    user_id: str


@dataclasses.dataclass
class ResetPasswordCommand(Command):
    email: str
    username: str
