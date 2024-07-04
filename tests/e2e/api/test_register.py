from typing import Any, List

import fastapi.testclient
import pytest
import fastapi
from icecream import ic
from tests import random_refs


@pytest.mark.usefixtures("request_bodies")
class TestRegister:
    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_register_successfully_returns_204(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]

        # act
        r = ic(client.post("/register", json=request_body))

        # assert
        assert r.status_code == fastapi.status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_register_invalid_password_returns_400(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body = request_bodies[0]
        request_body["password"] = random_refs.random_invalid_password()

        # act
        r = ic(client.post("/register", json=request_body))

        # assert
        assert r.status_code == fastapi.status.HTTP_400_BAD_REQUEST
        assert r.json()["detail"] == "Invalid password"

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [2], indirect=True)
    def test_register_email_already_existed_returns_409(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body_1 = request_bodies[0]
        request_body_2 = request_bodies[1]
        request_body_2["email"] = request_body_1["email"]
        r = ic(client.post("/register", json=request_body_1))

        # act
        r = ic(client.post("/register", json=request_body_2))

        # assert
        assert r.status_code == fastapi.status.HTTP_409_CONFLICT
        assert r.json()["detail"] == f"Email {request_body_1['email']} already existed"

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [2], indirect=True)
    def test_register_username_already_existed_returns_409(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body_1 = request_bodies[0]
        request_body_2 = request_bodies[1]
        request_body_2["username"] = request_body_1["username"]
        r = ic(client.post("/register", json=request_body_1))

        # act
        r = ic(client.post("/register", json=request_body_2))

        # assert
        assert r.status_code == fastapi.status.HTTP_409_CONFLICT
        assert r.json()["detail"] == f"Username {request_body_1['username']} already existed"
