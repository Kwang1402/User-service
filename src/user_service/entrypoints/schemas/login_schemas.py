import pydantic


class Token(pydantic.BaseModel):
    access_token: str
    toke_type: str
