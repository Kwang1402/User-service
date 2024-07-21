from typing import Any, List
from pathlib import Path

import fastapi.testclient
import pytest
import fastapi
from icecream import ic


@pytest.mark.usefixtures("request_bodies")
class TestFriend:
    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [2], indirect=True)
    def test_send_friend_request_returns_201(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body_1 = request_bodies[0]
        request_body_2 = request_bodies[1]
        r = ic(client.post("/register", json=request_body_1))
        r = ic(client.post("/register", json=request_body_2))
        form_data_1 = {
            "username": request_body_1["username"],
            "password": request_body_1["password"],
        }
        form_data_2 = {
            "username": request_body_2["username"],
            "password": request_body_2["password"],
        }

        r = ic(client.post("/login", data=form_data_1))
        user_id_1 = r.json()["detail"]["user_id"]

        r = ic(client.post("/login", data=form_data_2))
        user_id_2 = r.json()["detail"]["user_id"]

        # act
        r = ic(
            client.post(
                "/friend-requests",
                json={"sender_id": user_id_1, "receiver_id": user_id_2},
            )
        )
        ic(r.__dict__)
        friend_request = r.json()["friend_request"]

        # assert
        assert r.status_code == fastapi.status.HTTP_201_CREATED
        assert friend_request["sender_id"] == user_id_1
        assert friend_request["receiver_id"] == user_id_2

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [2], indirect=True)
    def test_get_friend_requests_returns_200(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body_1 = request_bodies[0]
        request_body_2 = request_bodies[1]
        r = ic(client.post("/register", json=request_body_1))
        r = ic(client.post("/register", json=request_body_2))
        form_data_1 = {
            "username": request_body_1["username"],
            "password": request_body_1["password"],
        }
        form_data_2 = {
            "username": request_body_2["username"],
            "password": request_body_2["password"],
        }

        r = ic(client.post("/login", data=form_data_1))
        user_id_1 = r.json()["detail"]["user_id"]

        r = ic(client.post("/login", data=form_data_2))
        user_id_2 = r.json()["detail"]["user_id"]

        r = ic(
            client.post(
                "/friend-requests",
                json={"sender_id": user_id_1, "receiver_id": user_id_2},
            )
        )

        r = ic(client.post(f"users/{user_id_2}/setup-2fa", json={"user_id": user_id_2}))
        email = request_body_2["email"]
        otp_file_path = Path(f"mock_emails/{email}.txt")
        with otp_file_path.open("r") as otp_file:
            otp_code = otp_file.read().strip()

        r = ic(
            client.patch(
                f"users/{user_id_2}/verify-2fa",
                json={"user_id": user_id_2, "otp_code": otp_code},
            )
        )

        r = ic(client.post("/login", data=form_data_2))
        token = r.json()["token"]
        access_token = token["access_token"]

        # act
        r = ic(
            client.get(
                "/friend-requests", headers={"Authorization": f"Bearer {access_token}"}
            )
        )
        ic(r.__dict__)

        # assert
        r.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [2], indirect=True)
    def test_accept_friend_request_returns_200(
        self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]
    ):
        # arrange
        request_body_1 = request_bodies[0]
        request_body_2 = request_bodies[1]
        r = ic(client.post("/register", json=request_body_1))
        r = ic(client.post("/register", json=request_body_2))
        form_data_1 = {
            "username": request_body_1["username"],
            "password": request_body_1["password"],
        }
        form_data_2 = {
            "username": request_body_2["username"],
            "password": request_body_2["password"],
        }

        r = ic(client.post("/login", data=form_data_1))
        user_id_1 = r.json()["detail"]["user_id"]

        r = ic(client.post("/login", data=form_data_2))
        user_id_2 = r.json()["detail"]["user_id"]

        r = ic(
            client.post(
                "/friend-requests",
                json={"sender_id": user_id_1, "receiver_id": user_id_2},
            )
        )

        r = ic(client.post(f"users/{user_id_2}/setup-2fa", json={"user_id": user_id_2}))
        email = request_body_2["email"]
        otp_file_path = Path(f"mock_emails/{email}.txt")
        with otp_file_path.open("r") as otp_file:
            otp_code = otp_file.read().strip()

        r = ic(
            client.patch(
                f"users/{user_id_2}/verify-2fa",
                json={"user_id": user_id_2, "otp_code": otp_code},
            )
        )

        r = ic(client.post("/login", data=form_data_2))
        token = r.json()["token"]
        access_token = token["access_token"]

        r = ic(
            client.get(
                "/friend-requests", headers={"Authorization": f"Bearer {access_token}"}
            )
        )

        friend_request = r.json()["friend_requests"][0]

        # act
        r = ic(
            client.post(
                f"/friend-requests/{friend_request['id']}/accept",
                json={"friend_request": friend_request},
            )
        )
        ic(r.__dict__)

        # assert
        assert r.status_code == fastapi.status.HTTP_200_OK
        assert r.json()["friend_request"] == friend_request
