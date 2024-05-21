import time
from pathlib import Path

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay
from fastapi.testclient import TestClient

from src.user_service.adapters.orm import start_mappers, metadata
from src.user_service import config
from user_service.entrypoints.fastapi_app import app
from tests import random_refs


@pytest.fixture
def data():
    yield {
        "username": random_refs.random_username(),
        "email": random_refs.random_email(),
        "password": random_refs.random_valid_password(),
    }


@pytest.fixture
def invalid_password_data():
    yield {
        "username": random_refs.random_username(),
        "email": random_refs.random_email(),
        "password": random_refs.random_invalid_password(),
    }


@pytest.fixture
def data2():
    yield {
        "username": random_refs.random_username(),
        "email": random_refs.random_email(),
        "password": random_refs.random_valid_password(),
    }


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture
def in_memory_sqlite_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def in_memory_sqlite_session_factory(in_memory_sqlite_db):
    yield sessionmaker(bind=in_memory_sqlite_db)


@pytest.fixture
def mappers():
    start_mappers()
    yield
    clear_mappers()


@retry(stop=stop_after_delay(10))
def wait_for_sqlite(engine):
    return engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp():
    return requests.get(config.get_api_url())


@pytest.fixture(scope="function")
def sqlite_db():
    engine = create_engine(config.get_sqlite_uri(), isolation_level="SERIALIZABLE")
    wait_for_sqlite(engine)
    metadata.create_all(engine)
    yield engine

    metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def sqlite_session_factory(sqlite_db):
    yield sessionmaker(bind=sqlite_db)


@pytest.fixture
def sqlite_session(sqlite_session_factory):
    return sqlite_session_factory()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/user_service/entrypoints/app.py").touch()
    time.sleep(0.5)
    wait_for_webapp()
