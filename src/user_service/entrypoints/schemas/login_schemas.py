import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class LoginResponse(pydantic.BaseModel):
    token: Token
