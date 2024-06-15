import pydantic
from datetime import date


class RegisterSchema(pydantic.BaseModel):
    username: str
    email: str
    password: str
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


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str
