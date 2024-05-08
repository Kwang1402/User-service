import pyotp
from flask_bcrypt import Bcrypt
from user_service.domains import models
from user_service.adapters import repository

bcrypt = Bcrypt()


def test_get_by_email(in_memory_sqlite_session_factory, data):
    session = in_memory_sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    secret_token = pyotp.random_base32()
    user = models.User(data["username"], data["email"], hashed_password, secret_token)
    repo.add(user)
    assert repo.get(models.User, email=user.email) == user
