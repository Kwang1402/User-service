import pydantic


class ResetPasswordBase(pydantic.BaseModel):
    username: str
    email: str


class ResetPasswordSchema(ResetPasswordBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")

    message: str


class ResetPasswordResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    reset_password: ResetPasswordSchema
