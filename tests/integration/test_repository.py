import pytest
from user_service.domains import models
from user_service.adapters import repository


def test_get_by_email(in_memory_sqlite_session_factory):
    session = in_memory_sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    user = models.User(
        "user",
        "user@email.com",
        "password123@",
    )
    repo.add(user)
    assert repo.get(models.User, email=user.email) == user
