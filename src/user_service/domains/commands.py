from user_service.domains import Message
from user_service.entrypoints import schemas


class Command(Message):
    pass


class RegisterCommand(Command, schemas.RegisterSchema):
    pass


class EnableTwoFactorAuthCommand(Command, schemas.EnableTwoFactorAuthSchema):
    user_id: str


class VerifyEnableTwoFactorAuthCommand(
    Command, schemas.VerifyEnableTwoFactorAuthSchema
):
    user_id: str


class LoginCommand(Command, schemas.LoginSchema):
    pass


class ResetPasswordCommand(Command, schemas.ResetPasswordSchema):
    pass


class AddFriendCommand(Command, schemas.AddFriendSchema):
    sender_id: str


class AcceptFriendRequestCommand(Command, schemas.AcceptFriendRequestSchema):
    pass


class DeclineFriendRequestCommand(Command, schemas.DeclineFriendRequestSchema):
    pass