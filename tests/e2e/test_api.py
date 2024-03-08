import pytest
from tests import random_refs
from user_service.domains import models
from flask_bcrypt import Bcrypt
import jwt

bcrypt = Bcrypt()


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
def data2():
    yield {
        "username": random_refs.random_username(),
        "email": random_refs.random_email(),
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
    assert bcrypt.check_password_hash(user.password, data["password"])

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
    data2,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    data2["email"] = data["email"]

    r = client.post("/register", json=data2)
    print(r.__dict__)
    assert r.status_code == 409
    assert r.json["error"] == f"Email {data2['email']} already existed"

    user_count = (
        sqlite_session.query(models.User).filter_by(email=data2["email"]).count()
    )
    assert user_count == 1

    cleanup_user.append(user.id)


def test_logged_in_successfully_returns_200(
    client,
    data,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    print(r.__dict__)
    assert r.status_code == 200
    assert r.json["token"] is not None
    cleanup_user.append(user.id)


def test_logged_in_incorrect_email_returns_401(
    client,
    data,
    sqlite_session,
):
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Incorrect email or password"


def test_logged_in_incorrect_password_returns_401(
    client,
    data,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    r = client.post(
        "/login",
        json={"email": data["email"], "password": random_refs.random_valid_password()},
    )
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Incorrect email or password"
    cleanup_user.append(user.id)


def test_get_user_successfully_returns_200(
    client,
    data,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    print(r.__dict__)
    assert r.status_code == 200
    assert r.json["token"] is not None

    token = r.json["token"]
    r = client.get(f"/user/{user.id}", headers={"Authorization": f"Bearer {token}"})
    print(r.__dict__)
    assert r.status_code == 200
    assert r.json["user"] == {"username": user.username, "email": user.email}
    cleanup_user.append(user.id)


def test_get_user_missing_token_returns_401(
    client,
    data,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    r = client.get(f"/user/{user.id}")
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Authorization token missing"
    cleanup_user.append(user.id)


def test_get_user_invalid_token_returns_401(
    client,
    data,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    invalid_token = jwt.encode({"user_id": user.id}, "random_key", algorithm="HS256")

    r = client.get(
        f"/user/{user.id}", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Invalid token"
    cleanup_user.append(user.id)


def test_get_user_unmatching_user_id_returns_401(
    client,
    data,
    data2,
    cleanup_user,
    sqlite_session,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    r = client.post("/register", json=data2)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user2 = sqlite_session.query(models.User).filter_by(email=data2["email"]).first()
    assert user2 is not None

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    print(r.__dict__)
    assert r.status_code == 200
    assert r.json["token"] is not None

    token = r.json["token"]
    r = client.get(f"/user/{user2.id}", headers={"Authorization": f"Bearer {token}"})
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Unauthorized access to user account"
    cleanup_user.append(user.id)
    cleanup_user.append(user2.id)


def test_reset_password_successfully_returns_200(
    client,
    data,
    sqlite_session,
    cleanup_user,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    r = client.post(
        "/reset-password", json={"email": user.email, "username": user.username}
    )
    sqlite_session.commit()
    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()

    print(r.__dict__)
    assert r.status_code == 200
    assert bcrypt.check_password_hash(user.password, r.json["new_password"])
    cleanup_user.append(user.id)

def test_reset_password_incorrect_email_returns_400(
    client,
    data,
    sqlite_session
):
    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data["username"]}
    )
    print(r.__dict__)
    assert r.status_code == 400
    assert r.json["error"] == "Incorrect email or username"

def test_reset_password_incorrect_username_returns_400(
    client,
    data,
    data2,
    sqlite_session,
    cleanup_user,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    user = sqlite_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None

    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data2["username"]}
    )
    print(r.__dict__)
    assert r.status_code == 400
    assert r.json["error"] == "Incorrect email or username"

    cleanup_user.append(user.id)