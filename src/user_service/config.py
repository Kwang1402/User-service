def get_mysql_uri():
    mysql_config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "1402",
        "database": "user_service_db",
    }

    mysql_uri = f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"

    return mysql_uri


def get_api_url():
    host = "localhost"
    port = 5000
    api_url = f"http://{host}:{port}"

    return api_url
