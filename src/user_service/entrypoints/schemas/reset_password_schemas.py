import pydantic


class ResetPasswordBase(pydantic.BaseModel):
    username: str
    email: str
