import pytest
import requests
from tests import random_refs
from user_service import config
from user_service.domains import models


@pytest.fixture
def data():
    yield {
        "username": random_refs.random_username(),
        "email": random_refs.random_email(),
        "password": random_refs.random_valid_password(),
        "backup_email": None,
        "gender": None,
        "date_of_birth": None,
    }


@pytest.fixture
def invalid_password_data():
    yield {
        "username": random_refs.random_username(),
        "email": random_refs.random_email(),
        "password": random_refs.random_invalid_password(),
        "backup_email": None,
        "gender": None,
        "date_of_birth": None,
    }


@pytest.fixture
def email_already_existed_data():
    yield {
        "username": random_refs.random_username(),
        "password": random_refs.random_valid_password(),
        "backup_email": None,
        "gender": None,
        "date_of_birth": None,
    }


@pytest.fixture
def cleanup_user(sqlite_session):
    users_to_cleanup = []

    yield users_to_cleanup

    for user_id in users_to_cleanup:
        user = sqlite_session.query(models.User).filter_by(id=user_id).first()
        if user:
            if user.profile:
                sqlite_session.delete(user.profile)
            sqlite_session.delete(user)

    sqlite_session.commit()


@pytest.mark.usefixtures("sqlite_db")
def test_registered_successfully_returns_201(
    client, data, cleanup_user, sqlite_session
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None
    assert user.username == data["username"]
    assert user.email == data["email"]
    assert user.password == data["password"]

    profile = user.profile
    assert profile.backup_email == data["backup_email"]
    assert profile.gender == data["gender"]
    assert profile.date_of_birth == data["date_of_birth"]

    cleanup_user.append(user.id)


@pytest.mark.usefixtures("sqlite_db")
def test_registered_invalid_password_returns_400(
    client, invalid_password_data, cleanup_user, sqlite_session
):
    r = client.post("/register", json=invalid_password_data)
    print(r.__dict__)
    assert r.status_code == 400
    assert r.json["error"] == f"Invalid password '{invalid_password_data['password']}'"

    user = (
        sqlite_session.query(models.User)
        .filter_by(email=invalid_password_data["email"])
        .first()
    )
    assert user is None

    if user is not None:
        cleanup_user.append(user.id)


def test_registered_email_already_existed_returns_409(
    client,
    data,
    email_already_existed_data,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    email_already_existed_data["email"] = data["email"]

    r = client.post("/register", json=email_already_existed_data)
    print(r.__dict__)
    assert r.status_code == 409
    assert (
        r.json["error"]
        == f"Email {email_already_existed_data['email']} already existed"
    )

    user_count = (
        sqlite_session.query(models.User)
        .filter_by(email=email_already_existed_data["email"])
        .count()
    )
    assert user_count == 1

    cleanup_user.append(user.id)
