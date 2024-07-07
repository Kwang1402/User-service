import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str
