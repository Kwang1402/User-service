from typing import Any, List
from pathlib import Path

import fastapi.testclient
import pytest
import fastapi
from icecream import ic


@pytest.mark.usefixtures
class Test2FA:
    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_login_2fa_not_enabled_returns_403(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        r = ic(client.post("/register", json=request_body))
        form_data = {
            "username": request_body["username"],
            "password": request_body["password"],
        }

        # act
        r = ic(client.post("/login", data=form_data))
        ic(r.__dict__)

        # assert
        assert r.status_code == fastapi.status.HTTP_403_FORBIDDEN
        assert (
            r.json()["detail"]["message"]
            == "Two-factor authentication required. Please set up 2FA"
        )
        assert r.json()["detail"]["user_id"]

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_enabled_2fa_successfully_returns_200(
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

        # act
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

        # assert
        assert r.status_code == fastapi.status.HTTP_200_OK
