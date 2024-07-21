import pytest
from tests import random_refs
from pathlib import Path
from fastapi import status
import jwt
import pyotp
import time
import random
from datetime import datetime, timedelta, timezone


@pytest.mark.usefixtures("mysql_db")
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


@pytest.mark.usefixtures("mysql_db")
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


@pytest.mark.usefixtures("mysql_db")
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


@pytest.mark.usefixtures("mysql_db")
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


@pytest.mark.usefixtures("mysql_db")
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


@pytest.mark.usefixtures("mysql_db")
def test_login_two_factor_auth_not_enabled_returns_202(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)

    # act
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_202_ACCEPTED
    assert "user_id" in r.json()


@pytest.mark.usefixtures("mysql_db")
def test_login_and_verify_enable_two_factor_auth_successfully_returns_200(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    # act
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"message": "Two-Factor Authentication successfully enabled"}


@pytest.mark.usefixtures("mysql_db")
def test_login_and_verify_enable_two_factor_auth_incorrect_otp_code_returns_400(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    # act
    otp_code = pyotp.TOTP(pyotp.random_base32()).now()
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": "Invalid OTP code"}


@pytest.mark.usefixtures("mysql_db")
def test_login_and_verify_enable_two_factor_auth_expired_otp_code_returns_400(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()
    time.sleep(30)

    # act
    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": "Invalid OTP code"}


@pytest.mark.usefixtures("mysql_db")
def test_logged_in_successfully_returns_200(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    # act
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert "token" in r.json()


@pytest.mark.usefixtures("mysql_db")
def test_logged_in_incorrect_email_returns_401(
    client,
    data,
):
    # arrange

    # act
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Incorrect email or password"}


@pytest.mark.usefixtures("mysql_db")
def test_logged_in_incorrect_password_returns_401(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)

    # act
    r = client.post(
        "/login",
        data={
            "username": data["email"],
            "password": random_refs.random_valid_password(),
        },
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Incorrect email or password"}


@pytest.mark.usefixtures("mysql_db")
def test_get_user_successfully_returns_200(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    token = r.json()["token"]

    # act
    r = client.get(
        f"/user/{user_id}", headers={"Authorization": f"Bearer {token['access_token']}"}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"user": {"username": data["username"], "email": data["email"]}}


@pytest.mark.usefixtures("mysql_db")
def test_get_user_missing_token_returns_401(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    # act
    r = client.get(f"/user/{user_id}")

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Not authenticated"}


@pytest.mark.usefixtures("mysql_db")
def test_get_user_invalid_token_returns_401(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    invalid_token = jwt.encode(
        {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        "random_key",
        algorithm="HS256",
    )

    # act
    r = client.get(
        f"/user/{user_id}", headers={"Authorization": f"Bearer {invalid_token}"}
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Signature verification failed"}


@pytest.mark.usefixtures("mysql_db")
def test_get_user_unmatching_user_id_returns_401(
    client,
    data,
    data2,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})

    r = client.post("/register", json=data2)
    r = client.post(
        "/login", data={"username": data2["email"], "password": data2["password"]}
    )
    user2_id = r.json()["user_id"]
    email = data2["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user2_id}/verify-enable-2fa", json={"otp_code": otp_code})

    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    token = r.json()["token"]

    # act
    r = client.get(
        f"/user/{user2_id}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": "Not authenticated"}


@pytest.mark.usefixtures("mysql_db")
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

    email = data["email"]
    new_password_file_path = Path(f"mock_emails/{email}.txt")
    with new_password_file_path.open("r") as new_password_file:
        new_password = new_password_file.read().strip()

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert new_password is not None


@pytest.mark.usefixtures("mysql_db")
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


@pytest.mark.usefixtures("mysql_db")
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


@pytest.mark.usefixtures("mysql_db")
def test_get_user_profile(
    client,
    data,
):
    # arrange
    r = client.post("/register", json=data)

    # act
    r = client.get(f"/user/profile/{data['username']}")

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("mysql_db")
def test_add_friend_successfully_returns_201(
    client,
    data,
    data2,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    token = r.json()["token"]

    r = client.post("/register", json=data2)

    r = client.get(f"/user/profile/{data2['username']}")

    user2_id = r.json()["user_id"]

    # act
    r = client.post(
        "/add-friend",
        json={"receiver_id": user2_id},
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json() == {"message": "Friend request sent"}


@pytest.mark.usefixtures("mysql_db")
def test_get_friend_requests_successfully_returns_200(
    client,
    data,
    data2,
):
    # arrange
    r = client.post("/register", json=data)
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]

    email = data["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user_id = r.json()["user_id"]
    token = r.json()["token"]

    r = client.post("/register", json=data2)
    r = client.post(
        "/login", data={"username": data2["email"], "password": data2["password"]}
    )

    user2_id = r.json()["user_id"]

    email = data2["email"]
    otp_file_path = Path(f"mock_emails/{email}.txt")
    with otp_file_path.open("r") as otp_file:
        otp_code = otp_file.read().strip()

    r = client.patch(f"/user/{user2_id}/verify-enable-2fa", json={"otp_code": otp_code})
    r = client.post(
        "/login", data={"username": data["email"], "password": data["password"]}
    )
    user2_id = r.json()["user_id"]
    token_2 = r.json()["token"]

    r = client.get(f"/user/profile/{data2['username']}")
    r = client.post(
        "/add-friend",
        json={"receiver_id": user2_id},
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )

    # act
    r = client.get(
        f"/friend-requests",
        headers={"Authorization": f"Bearer {token_2['access_token']}"},
    )

    # assert
    print(r.__dict__)
    assert r.status_code == status.HTTP_200_OK
    assert r.json()[0]["sender_id"] == user_id
    assert r.json()[0]["receiver_id"] == user2_id
