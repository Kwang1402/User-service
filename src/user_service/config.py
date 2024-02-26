import sqlalchemy


def get_sqlite_uri():
    sqlite_uri = "sqlite:///user_service.db"
    return sqlite_uri


def get_api_url():
    host = "localhost"
    port = 5000
    api_url = f"http://{host}:{port}"

    return api_url
