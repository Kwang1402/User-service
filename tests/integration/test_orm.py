from datetime import datetime
import uuid
from sqlalchemy import text
from user_service.domains import models


def test_user_mapper_can_load_users(session):
    user_data = {
        "id": str(uuid.uuid4()),
        "username": "user123",
        "email": "example123@gmail.com",
        "password": "password123@",
        "locked": False,
        "created_time": datetime.utcnow(),
        "updated_time": datetime.utcnow(),
    }
    insert_statement = text(
        """
        INSERT INTO users (id, username, email, password, locked, created_time, updated_time)
        VALUES (:id, :username, :email, :password, :locked, :created_time, :updated_time)
        """
    )
    session.execute(insert_statement, user_data)
    expected = [models.User(**user_data)]
    assert session.query(models.User).all() == expected


def test_user_mapper_can_save_users(session):
    new_user = models.User(
        str(uuid.uuid4()),
        "user456",
        "example456@gmail.com",
        "password456#",
        False,
        datetime.utcnow(),
        datetime.utcnow(),
    )
    session.add(new_user)
    session.commit()

    select_statement = text("SELECT * FROM users")
    rows = list(session.execute(select_statement))
    assert rows == [
        (
            new_user.id,
            new_user.username,
            new_user.email,
            new_user.password,
            new_user.locked,
            new_user.created_time,
            new_user.updated_time,
        )
    ]
    delete_statement = text(
        """
        DELETE FROM users
        WHERE id = :id
        """
    )
    session.execute(delete_statement, {"id": new_user.id})
    session.commit()
