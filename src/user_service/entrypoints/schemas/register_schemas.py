from datetime import date, datetime
from typing import Optional

import pydantic


class RegisterBase(pydantic.BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]
    backup_email: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[date]


class RegisterSchema(RegisterBase):
    model_config = pydantic.ConfigDict(from_attributes=True, extra="allow")

    id: str
    created_time: datetime = pydantic.Field(default_factory=datetime.now)
    updated_time: datetime = pydantic.Field(default_factory=datetime.now)


class RegisterResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    register: RegisterSchema
