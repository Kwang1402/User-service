import time
import pytest
import requests
from pathlib import Path
from requests.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from src.user_service.adapters.orm import start_mappers, metadata
from src.user_service import config


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    # engine = create_engine(
    #     "mysql+mysqlconnector://root:1402@localhost/user_service_test_db", echo=True
    # )
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(test_db):
    start_mappers()
    yield sessionmaker(bind=test_db)()
    clear_mappers()


def wait_for_mysql(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("MySQL never came up")


def wait_for_webapp():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
        pytest.fail("API never came up")


# @pytest.fixture(scope="session")
@pytest.fixture
def mysql_db(test_db):
    # engine = create_engine(config.get_mysql_uri())
    engine = test_db
    wait_for_mysql(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def mysql_session(mysql_db):
    start_mappers()
    yield sessionmaker(bind=mysql_db)()
    clear_mappers()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/user_service/entrypoints/app.py").touch()
    time.sleep(0.5)
    wait_for_webapp()
