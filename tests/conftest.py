import time
from pathlib import Path
from typing import Any, List, Generator

import pytest
import requests
from sqlalchemy import text, MetaData, create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay
from fastapi.testclient import TestClient

from src.user_service.adapters.orm import start_mappers, metadata
from src.user_service import config
from user_service.entrypoints.rest.fastapi_app import app
from tests import random_refs


def create_request_body() -> dict[str, Any]:
    return {
        "username": random_refs.random_username(),
        "email": random_refs.random_email(),
        "password": random_refs.random_valid_password(),
        "first_name": None,
        "last_name": None,
        "backup_email": None,
        "gender": None,
        "date_of_birth": None,
    }


@pytest.fixture
def request_bodies(request) -> Generator[List[dict[str, Any]], Any, None]:
    num_bodies = request.param
    bodies = [create_request_body() for _ in range(num_bodies)]
    yield bodies


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture
def sqlite_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session_factory(sqlite_db):
    yield sessionmaker(bind=sqlite_db)


@pytest.fixture
def mappers():
    start_mappers()
    yield
    clear_mappers()


@retry(stop=stop_after_delay(10))
def wait_for_mysql(engine):
    return engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp():
    return requests.get(config.get_api_url())


def cleanup_database(engine):
    meta = MetaData()
    meta.reflect(bind=engine)

    with engine.begin() as conn:
        # Disable foreign key checks
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

        for table in reversed(meta.sorted_tables):
            conn.execute(text(f"TRUNCATE TABLE {table.name}"))

        # Enable foreign key checks
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))


@pytest.fixture(scope="session")
def mysql_db():
    engine = create_engine(config.get_mysql_uri(), isolation_level="SERIALIZABLE")
    wait_for_mysql(engine)
    metadata.create_all(engine)
    cleanup_database(engine)
    yield engine


@pytest.fixture
def mysql_session_factory(mysql_db):
    yield sessionmaker(bind=mysql_db)


@pytest.fixture
def mysql_session(mysql_session_factory):
    return mysql_session_factory()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/user_service/entrypoints/fastapi_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp()
