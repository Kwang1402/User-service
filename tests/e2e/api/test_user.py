from typing import Any, List
from pathlib import Path

import fastapi.testclient
import pytest
import fastapi
from icecream import ic


@pytest.mark.usefixtures
class TestUser:
    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_get_user_successfully_returns_200(
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
        r = ic(client.post("/login", data=form_data))
        token = r.json()["token"]
        access_token = token["access_token"]

        # act
        r = ic(
            client.get(
                f"users/{user_id}", headers={"Authorization": f"Bearer {access_token}"}
            )
        )
        ic(r.__dict__)

        # assert
        assert r.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_get_user_missing_token_returns_401(
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
        r = ic(client.get(f"users/{user_id}"))
        ic(r.__dict__)

        # assert
        assert r.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
        assert r.json()["detail"] == "Not authenticated"
