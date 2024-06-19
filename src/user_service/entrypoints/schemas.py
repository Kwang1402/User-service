import pydantic
from datetime import date


class RegisterSchema(pydantic.BaseModel):
    username: str
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
    backup_email: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None


class EnableTwoFactorAuthSchema(pydantic.BaseModel):
    pass


class VerifyEnableTwoFactorAuthSchema(pydantic.BaseModel):
    otp_code: str


class LoginSchema(pydantic.BaseModel):
    email: str
    password: str


class ResetPasswordSchema(pydantic.BaseModel):
    email: str
    username: str


class AddFriendSchema(pydantic.BaseModel):
    receiver_id: str


class AcceptFriendRequestSchema(pydantic.BaseModel):
    friend_request_id: str


class DeclineFriendRequestSchema(pydantic.BaseModel):
    friend_request_id: str


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str
