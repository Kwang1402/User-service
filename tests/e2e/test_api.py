import pytest
from icecream import ic
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
def cleanup_user(mysql_session):
    users_to_cleanup = []

    yield users_to_cleanup

    for user_id in users_to_cleanup:
        user = mysql_session.query(models.User).filter_by(id=user_id).first()
        if user:
            if user.profile:
                mysql_session.delete(user.profile)
            mysql_session.delete(user)

    mysql_session.commit()


@pytest.mark.usefixtures("mysql_db")
# @pytest.mark.usefixtures("restart_api")
def test_registered_successfully_returns_201(data, cleanup_user, mysql_session):
    url = config.get_api_url()
    r = requests.post(f"{url}/register", json=data)
    print(r.__dict__)
    assert r.status_code == 201
    assert r.json() == {"message": "User successfully registered"}

    user = mysql_session.query(models.User).filter_by(email=data["email"]).first()
    assert user is not None
    profile = user.profile
    cleanup_user.append(user.id)


@pytest.mark.usefixtures("mysql_db")
@pytest.mark.usefixtures("restart_api")
def test_registered_invalid_password_returns_400(
    invalid_password_data, cleanup_user, mysql_session
):
    url = config.get_api_url()
    r = requests.post(f"{url}/register", json=invalid_password_data)
    print(r.__dict__)
    assert r.status_code == 400
    assert r.json() == {"error": f"Invalid password '{invalid_password_data['password']}'"}

    user = mysql_session.query(models.User).filter_by(email=invalid_password_data["email"]).first()
    assert user is None

    if user is not None:
        cleanup_user.append(user.id)
