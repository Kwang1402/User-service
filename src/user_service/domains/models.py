from __future__ import annotations
from datetime import date, datetime
import dataclasses
import uuid
from flask_bcrypt import Bcrypt
import string
import random
import jwt
from user_service.config import SECRET_KEY

bcrypt = Bcrypt()

def random_valid_password(length=12):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation
    all_characters = lowercase_letters + uppercase_letters + digits + special_characters

    password = "".join(random.choice(all_characters) for _ in range(length - 4))
    password += random.choice(lowercase_letters)
    password += random.choice(uppercase_letters)
    password += random.choice(digits)
    password += random.choice(special_characters)

    return password

@dataclasses.dataclass
class BaseModel:
    def __init__(
        self,
    ):
        self.id = str(uuid.uuid4())
        self.created_time = datetime.now()
        self.updated_time = datetime.now()


class User(BaseModel):
    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        locked: bool = False,
    ):
        super().__init__()
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")
        self.locked = locked
        self.events = []

    def __repr__(self):
        return f"<User {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
    
    def check_password(self, password) -> bool:
        return bcrypt.check_password_hash(self.password, password)
    
    def generate_token(self):
        return jwt.encode({"user_id": self.id}, SECRET_KEY, algorithm="HS256")

    def change_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def reset_password(self) -> string:
        new_password = random_valid_password()
        self.change_password(new_password)
        return new_password


class Profile(BaseModel):
    def __init__(
        self,
        user_id: str,
        backup_email: str = None,
        gender: str = None,
        date_of_birth: date = None,
    ):
        super().__init__()
        self.user_id = user_id
        self.backup_email = backup_email
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.events = []

    def __repr__(self):
        return f"<Profile {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
