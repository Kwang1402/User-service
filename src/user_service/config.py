import sqlalchemy

SECRET_KEY = "sample_user_service_secret_key"


def get_mysql_uri():
    mysql_uri = "mysql+pymysql://test_user:test_password@localhost:3307/test_db"
    return mysql_uri


def get_api_url():
    host = "localhost"
    port = 5000
    api_url = f"http://{host}:{port}"

    return api_url
