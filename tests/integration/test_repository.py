from user_service.domains import models
from user_service.adapters import repository


def test_get_by_email(in_memory_sqlite_session_factory, data):
    session = in_memory_sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    user = models.User(data["username"], data["email"], data["password"])
    repo.add(user)
    assert repo.get(models.User, email=user.email) == user
