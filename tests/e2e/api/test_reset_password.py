from typing import Any, List
from pathlib import Path

import fastapi.testclient
import pytest
import fastapi
from icecream import ic


@pytest.mark.usefixtures
class TestResetPassword:
    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_reset_password_successfully_returns_200(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        r = ic(client.post("/register", json=request_body))

        # act
        r = ic(
            client.post(
                "/reset-password",
                json={
                    "email": request_body["email"],
                    "username": request_body["username"],
                },
            )
        )

        email = request_body["email"]
        new_password_file_path = Path(f"mock_emails/{email}.txt")
        with new_password_file_path.open("r") as new_password_file:
            new_password = new_password_file.read().strip()

        # assert
        assert r.status_code == fastapi.status.HTTP_200_OK
        assert new_password is not None

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_reset_password_incorrect_email_returns_200(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]

        # act
        r = ic(
            client.post(
                "/reset-password",
                json={
                    "email": request_body["email"],
                    "username": request_body["username"],
                },
            )
        )

        # assert
        assert r.status_code == fastapi.status.HTTP_400_BAD_REQUEST
        assert r.json()["detail"] == "Incorrect email or username"
