from typing import Any, List
from pathlib import Path

import fastapi.testclient
import pytest
import fastapi
from icecream import ic

from tests import random_refs


@pytest.mark.usefixtures
class TestLogin:
    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_login_with_username_successfully_returns_200(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        r = ic(client.post("/register", json=request_body))
        form_data = {
            "username": request_body["username"],
            "password": request_body["password"],
        }
        r = ic(client.post("/login", data=form_data))
        user_id = r.json()["detail"]["user_id"]

        r = ic(client.post(f"users/{user_id}/setup-2fa", json={"user_id": user_id}))
        email = request_body["email"]
        otp_file_path = Path(f"mock_emails/{email}.txt")
        with otp_file_path.open("r") as otp_file:
            otp_code = otp_file.read().strip()

        r = ic(
            client.patch(
                f"users/{user_id}/verify-2fa",
                json={"user_id": user_id, "otp_code": otp_code},
            )
        )

        # act
        r = ic(client.post("/login", data=form_data))
        ic(r.__dict__)
        token = r.json()["token"]

        # assert
        assert r.status_code == fastapi.status.HTTP_200_OK
        assert token["access_token"]
        assert token["token_type"] == "bearer"

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_login_with_email_successfully_returns_200(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        r = ic(client.post("/register", json=request_body))
        form_data = {
            "username": request_body["email"],
            "password": request_body["password"],
        }
        r = ic(client.post("/login", data=form_data))
        user_id = r.json()["detail"]["user_id"]

        r = ic(client.post(f"users/{user_id}/setup-2fa", json={"user_id": user_id}))
        email = request_body["email"]
        otp_file_path = Path(f"mock_emails/{email}.txt")
        with otp_file_path.open("r") as otp_file:
            otp_code = otp_file.read().strip()

        r = ic(
            client.patch(
                f"users/{user_id}/verify-2fa",
                json={"user_id": user_id, "otp_code": otp_code},
            )
        )

        # act
        r = ic(client.post("/login", data=form_data))
        ic(r.__dict__)
        token = r.json()["token"]

        # assert
        assert r.status_code == fastapi.status.HTTP_200_OK
        assert token["access_token"]
        assert token["token_type"] == "bearer"

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_login_with_incorrect_username_returns_401(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        form_data = {
            "username": request_body["username"],
            "password": request_body["password"],
        }

        # act
        r = ic(client.post("/login", data=form_data))

        # assert
        assert r.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
        assert r.json()["detail"] == "Incorrect username or password"

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_login_with_incorrect_email_returns_401(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        form_data = {
            "username": request_body["email"],
            "password": request_body["password"],
        }

        # act
        r = ic(client.post("/login", data=form_data))

        # assert
        assert r.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
        assert r.json()["detail"] == "Incorrect username or password"

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_login_with_incorrect_password_returns_401(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        r = ic(client.post("/register", json=request_body))
        form_data = {
            "username": request_body["email"],
            "password": request_body["password"],
        }
        r = ic(client.post("/login", data=form_data))
        user_id = r.json()["detail"]["user_id"]

        r = ic(client.post(f"users/{user_id}/setup-2fa", json={"user_id": user_id}))
        email = request_body["email"]
        otp_file_path = Path(f"mock_emails/{email}.txt")
        with otp_file_path.open("r") as otp_file:
            otp_code = otp_file.read().strip()

        r = ic(
            client.patch(
                f"users/{user_id}/verify-2fa",
                json={"user_id": user_id, "otp_code": otp_code},
            )
        )

        form_data["password"] = random_refs.random_valid_password()

        # act
        r = ic(client.post("/login", data=form_data))
        ic(r.__dict__)

        # assert
        assert r.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
        assert r.json()["detail"] == "Incorrect username or password"
