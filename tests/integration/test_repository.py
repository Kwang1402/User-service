import pytest
from user_service.domains import models
from user_service.adapters import repository


def test_get_by_email(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    user = models.User(
        "user",
        "user@email.com",
        "password123@",
    )
    repo.add(user)
    assert repo.get_by_email("user@email.com") == user
