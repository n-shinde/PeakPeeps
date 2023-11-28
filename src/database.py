import os
import dotenv
import sqlalchemy
from sqlalchemy import create_engine
from src import database as db


def database_connection_url():
    dotenv.load_dotenv()
    deployment_type = os.environ.get("DEPLOYMENT_TYPE")
    if deployment_type == "development":
        return os.environ.get("DEVELOPMENT_POSTGRES_URI")
    return os.environ.get("POSTGRES_URI")


print(os.environ.get("POSTGRES_URI"))

engine = create_engine(database_connection_url(), pool_pre_ping=True)
read_repeatable_engine = create_engine(
    database_connection_url(), pool_pre_ping=True, isolation_level="REPEATABLE READ"
)
