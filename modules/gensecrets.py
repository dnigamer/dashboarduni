import os
import json

secrets = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "login": os.environ.get("DB_LOGIN"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_DATABASE"),
}

with open("../secrets.json", "w") as f:
    json.dump(secrets, f)
