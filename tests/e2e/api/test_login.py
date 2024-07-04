from typing import Any, List, Generator

import fastapi.testclient
import pytest
import fastapi
from icecream import ic
from tests import random_refs

@pytest.mark.usefixtures
class TestLogin:
    @pytest.mark.usefixtures("mysql_db")
    @pytest.mark.parametrize("request_bodies", [1], indirect=True)
    def test_login_2fa_not_enabled_redirect_setup_2fa_returns_202(self, client: fastapi.testclient, request_bodies: List[dict[str, Any]]):
        # arrange
        request_body = request_bodies[0]
        r = ic(client.post("/register", json=request_body))
        form_data = {
            "username": request_body["username"],
            "password": request_body["password"],
        }

        # act
        r = ic(client.post("/login", data=form_data))

        # assert
        assert r.status_code == fastapi.status.HTTP_202_ACCEPTED