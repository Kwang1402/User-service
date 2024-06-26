from typing import Any, Generator

import pytest
from fastapi import testclient, status

from tests import random_refs


class TestRegister:
    @pytest.fixture
    def request_body(self) -> Generator[dict[str, Any], Any, None]:
        yield {
            "username": random_refs.random_username(),
            "email": random_refs.random_email(),
            "password": random_refs.random_valid_password(),
            "first_name": None,
            "last_name": None,
            "backup_email": None,
            "gender": None,
            "date_of_birth": None,
        }

    @pytest.mark.usefixtures("mysql_db")
    def test_registered_successfully_returns_201(
        self, client: testclient, request_body: dict[str, Any]
    ):
        # arrange
        expected_response = request_body | {}

        # act
        r = client.post("/register", json=request_body)

        # assert
        print(r.__dict__)
        assert r.status_code == status.HTTP_201_CREATED
        resource_json = r.json()["register"]

        assert set(expected_response.keys()).issubset(resource_json.keys())
        for key in {"id", "created_time", "updated_time"}:
            assert resource_json.get(key)
