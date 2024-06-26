from datetime import datetime
import pydantic


class UserBase(pydantic.BaseModel):
    username: str
    password: str
    email: str


class UserSchema(UserBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")

    id: str
    created_time: datetime = pydantic.Field(default_factory=datetime.now)
    updated_time: datetime = pydantic.Field(default_factory=datetime.now)


class UserReponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    user: UserSchema


class ProfileBase(pydantic.BaseModel):
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str


class ProfileSchema(ProfileBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")

    id: str
    friends: int
    followers: int
    created_time: datetime = pydantic.Field(default_factory=datetime.now)
    updated_time: datetime = pydantic.Field(default_factory=datetime.now)


class ProfileReponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    profile: ProfileSchema


class SetupTwoFactorAuthBase(pydantic.BaseModel):
    username: str


class SetupTwoFactorAuthSchema(SetupTwoFactorAuthBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")

    message: str


class SetupTwoFactorAuthResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    setup_two_factor_auth: SetupTwoFactorAuthSchema


class VerifyTwoFactorAuthBase(pydantic.BaseModel):
    username: str
    otp_code: str


class VerifyTwoFactorAuthSchema(VerifyTwoFactorAuthBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")

    message: str


class VerifyTwoFactorAuthResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    verify_two_factor_auth: VerifyTwoFactorAuthSchema
