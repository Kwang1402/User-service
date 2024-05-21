import pytest
from tests import random_refs
from fastapi import status
from flask_bcrypt import Bcrypt
import jwt
import pyotp
import time
import json
import random

bcrypt = Bcrypt()


@pytest.mark.usefixtures("sqlite_db")
def test_registered_successfully_returns_201(
    client,
    data,
):
    # arrange

    # act
    r = client.post("/register", json=data)

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json() == {"message": "User successfully registered"}

@pytest.mark.usefixtures("sqlite_db")
def test_registered_missing_field_returns_422(
    client,
    data,
):
    # arrange
    del_key = random.choice(list(data.keys()))
    del data[del_key]

    # act
    r = client.post("/register", json=data)

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.usefixtures("sqlite_db")
def test_registered_not_json_returns_422(
    client,
    data,
):
    # arrange
    
    # act
    r = client.post("/register", content=str(data))

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.usefixtures("sqlite_db")
def test_registered_invalid_password_returns_400(
    client,
    invalid_password_data,
):
    # arrange

    # act
    r = client.post("/register", json=invalid_password_data)

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": "Invalid password"}


@pytest.mark.usefixtures("sqlite_db")
def test_registered_email_already_existed_returns_409(
    client,
    data,
    data2,
):
    # arrange
    r = client.post("/register", json=data)
    data2["email"] = data["email"]

    # act
    r = client.post("/register", json=data2)

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json() == {"detail": f"Email {data2['email']} already existed"}


@pytest.mark.usefixtures("sqlite_db")
def test_login_two_factor_auth_not_enabled_returns_202(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)

    # act
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_202_ACCEPTED
    assert "user_id" in r.json()
    assert "otp_code" in r.json()


@pytest.mark.usefixtures("sqlite_db")
def test_login_and_verify_enable_two_factor_auth_successfully_returns_200(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]

    # act
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"message": "Two-Factor Authentication successfully enabled"}


@pytest.mark.usefixtures("sqlite_db")
def test_login_and_verify_enable_two_factor_auth_incorrect_otp_code_returns_400(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    # act
    otp_code = pyotp.TOTP(pyotp.random_base32()).now()
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": "Invalid OTP code"}


@pytest.mark.usefixtures("sqlite_db")
def test_login_and_verify_enable_two_factor_auth_expired_otp_code_returns_400(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]
    time.sleep(30)

    # act
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": "Invalid OTP code"}


@pytest.mark.usefixtures("sqlite_db")
def test_logged_in_successfully_returns_200(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # act
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert "token" in r.json()


@pytest.mark.usefixtures("sqlite_db")
def test_logged_in_incorrect_email_returns_401(
    client,
    data,
):
    # arrange

    # act
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Incorrect email or password"}


@pytest.mark.usefixtures("sqlite_db")
def test_logged_in_incorrect_password_returns_401(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)

    # act
    r = client.post(
        "/login",
        json={"email": data["email"], "password": random_refs.random_valid_password()},
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Incorrect email or password"}


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_successfully_returns_200(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    token = r.json()["token"]

    # act
    r = client.get(f"/user/{user_id}", headers={"Authorization": f"Bearer {token}"})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"user": {"username": data["username"], "email": data["email"]}}


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_missing_token_returns_401(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    # act
    r = client.get(f"/user/{user_id}")

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Authorization token missing"}


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_invalid_token_returns_401(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    invalid_token = jwt.encode({"user_id": user_id}, "random_key", algorithm="HS256")

    # act
    r = client.get(
        f"/user/{user_id}", headers={"Authorization": f"Bearer {invalid_token}"}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Invalid token"}


@pytest.mark.usefixtures("sqlite_db")
def test_get_user_unmatching_user_id_returns_401(
    client,
    data,
    data2,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    r = client.post("/register", json=data2)
    r = client.post(
        "/login", json={"email": data2["email"], "password": data2["password"]}
    )
    user2_id = r.json()["user_id"]
    otp_code = r.json()["otp_code"]
    r = client.patch(f"/user/{user2_id}/verify-enable-2fa", json={"otp_code": otp_code})

    r = client.post(
        "/login", json={"email": data["email"], "password": data["password"]}
    )
    token = r.json()["token"]

    # act
    r = client.get(f"/user/{user2_id}", headers={"Authorization": f"Bearer {token}"})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Unauthorized access to user account"}


@pytest.mark.usefixtures("sqlite_db")
def test_reset_password_successfully_returns_200(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)

    # act
    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data["username"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert "new_password" in r.json()


@pytest.mark.usefixtures("sqlite_db")
def test_reset_password_incorrect_email_returns_400(
    client,
    data,
):
    # arrange

    # act
    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data["username"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": "Incorrect email or username"}


@pytest.mark.usefixtures("sqlite_db")
def test_reset_password_incorrect_username_returns_400(
    client,
    data,
    data2,
):
    # arrange
    r = client.post("/register", json=data)

    # act
    r = client.post(
        "/reset-password", json={"email": data["email"], "username": data2["username"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": "Incorrect email or username"}
