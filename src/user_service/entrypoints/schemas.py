import pydantic
from datetime import date

class RegisterRequest(pydantic.BaseModel):
    username: str
    email: str
    password: str
    backup_email: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None

class LoginRequest(pydantic.BaseModel):
    email: str
    password: str

class ResetPasswordRequest(pydantic.BaseModel):
    email: str
    username: str

class VerifyEnableTwoFactorAuthRequest(pydantic.BaseModel):
    otp_code: str