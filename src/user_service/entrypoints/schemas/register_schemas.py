from datetime import date
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
