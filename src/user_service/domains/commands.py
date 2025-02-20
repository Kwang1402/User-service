from user_service.domains import Message
from user_service.entrypoints.schemas import (
    friend_schemas,
    register_schemas,
    reset_password_schemas,
    user_schemas,
)


class Command(Message):
    """"""


class RegisterCommand(Command, register_schemas.RegisterBase):
    """"""


class SetupTwoFactorAuthCommand(Command, user_schemas.SetupTwoFactorAuthBase):
    """"""


class VerifyTwoFactorAuthCommand(Command, user_schemas.VerifyTwoFactorAuthBase):
    """"""


class LoginCommand(Command):
    username: str
    password: str


class ResetPasswordCommand(Command, reset_password_schemas.ResetPasswordBase):
    """"""


class FriendRequestCommand(Command, friend_schemas.FriendRequestBase):
    """"""


class AcceptFriendRequestCommand(Command, friend_schemas.AcceptFriendRequestBase):
    """"""


class DeclineFriendRequestCommand(Command, friend_schemas.DeclineFriendRequestBase):
    """"""
