import pytest
from tests import random_refs
from user_service.domains import models
from flask_bcrypt import Bcrypt
import jwt

bcrypt = Bcrypt()


@pytest.fixture
def cleanup_user(sqlite_session):
    users_to_cleanup = []

    yield users_to_cleanup

    for user_email in users_to_cleanup:
        user = sqlite_session.query(models.User).filter_by(email=user_email).first()
        profile = (
            sqlite_session.query(models.Profile)
            .filter_by(user_id=user.id)
            .one_or_none()
        )
        if profile:
            sqlite_session.delete(profile)
        if user:
            sqlite_session.delete(user)

    sqlite_session.commit()


@pytest.mark.usefixtures("sqlite_db")
def test_registered_successfully_returns_201(
    client,
    data,
    cleanup_user,
):
    r = client.post("/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json["message"] == "User successfully registered"

    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_registered_invalid_password_returns_400(
    client,
    invalid_password_data,
):
    r = client.post("/register", json=invalid_password_data)
    print(r.__dict__)
    assert r.status_code == 400
    assert r.json["error"] == "Invalid password"


@pytest.mark.usefixtures("sqlite_db")
def test_registered_email_already_existed_returns_409(
    client,
    data,
    data2,
    cleanup_user,
):
    r = client.post("/register", json=data)

    data2["email"] = data["email"]

    r = client.post("/register", json=data2)
    print(r.__dict__)
    assert r.status_code == 409
    assert r.json["error"] == f"Email {data2['email']} already existed"

    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_logged_in_successfully_returns_200(
    client,
    data,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    print(r.__dict__)
    assert r.status_code == 200
    assert r.json["token"] is not None
    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_logged_in_incorrect_email_returns_401(
    client,
    data,
):
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Incorrect email or password"


@pytest.mark.usefixtures("sqlite_db")
def test_logged_in_incorrect_password_returns_401(
    client,
    data,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post(
        "/login",
        json={"email": data["email"], "password": random_refs.random_valid_password()},
    )
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Incorrect email or password"
    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_successfully_returns_200(
    client,
    data,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )

    user_id = r.json["user_id"]
    token = r.json["token"]
    r = client.get(f"/user/{user_id}", headers={"Authorization": f"Bearer {token}"})
    print(r.__dict__)
    assert r.status_code == 200
    assert r.json["user"] == {"username": data["username"], "email": data["email"]}
    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_missing_token_returns_401(
    client,
    data,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )

    user_id = r.json["user_id"]

    r = client.get(f"/user/{user_id}")
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Authorization token missing"
    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_invalid_token_returns_401(
    client,
    data,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )

    user_id = r.json["user_id"]

    invalid_token = jwt.encode({"user_id": user_id}, "random_key", algorithm="HS256")

    r = client.get(
        f"/user/{user_id}", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Invalid token"
    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_unmatching_user_id_returns_401(
    client,
    data,
    data2,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post("/register", json=data2)

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )

    token = r.json["token"]

    r = client.post(
        "/login", json={"email": data2["email"], "password": data2["password"]}
    )

    user2_id = r.json["user_id"]

    r = client.get(f"/user/{user2_id}", headers={"Authorization": f"Bearer {token}"})
    print(r.__dict__)
    assert r.status_code == 401
    assert r.json["error"] == "Unauthorized access to user account"
    cleanup_user.append(data["email"])
    cleanup_user.append(data2["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_reset_password_successfully_returns_200(
    client,
    data,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data["username"]}
    )

    print(r.__dict__)
    assert r.status_code == 200
    assert r.json["new_password"] is not None
    cleanup_user.append(data["email"])


@pytest.mark.usefixtures("sqlite_db")
def test_reset_password_incorrect_email_returns_400(
    client,
    data,
):
    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data["username"]}
    )
    print(r.__dict__)
    assert r.status_code == 400
    assert r.json["error"] == "Incorrect email or username"


@pytest.mark.usefixtures("sqlite_db")
def test_reset_password_incorrect_username_returns_400(
    client,
    data,
    data2,
    cleanup_user,
):
    r = client.post("/register", json=data)

    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data2["username"]}
    )
    print(r.__dict__)
    assert r.status_code == 400
    assert r.json["error"] == "Incorrect email or username"

    cleanup_user.append(data["email"])
