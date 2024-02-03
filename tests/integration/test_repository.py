from user_service.domains import models
from user_service.adapters import repository
import uuid
from datetime import datetime
from sqlalchemy import text


def test_repository_can_save_an_user(session):
    user = models.User(
        str(uuid.uuid4()),
        "user456",
        "example456@email.com",
        "password456#",
        False,
        datetime.utcnow(),
        datetime.utcnow(),
    )
    repo = repository.SqlAlchemyRepository(session, models.User)
    repo.add(user)
    session.commit()

    select_statement = text("SELECT * FROM users")

    rows = session.execute(select_statement)

    assert list(rows) == [
        (
            user.id,
            user.username,
            user.email,
            user.password,
            user.locked,
            user.created_time,
            user.updated_time,
        )
    ]

    delete_statement = text(
        """
        DELETE FROM users
        WHERE id = :id
        """
    )
    session.execute(delete_statement, {"id": user.id})
    session.commit()
