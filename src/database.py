import os
import dotenv
import sqlalchemy
from sqlalchemy import create_engine
from src import database as db

def database_connection_url():
    dotenv.load_dotenv()
    return os.environ.get("POSTGRES_URI")

print(os.environ.get("POSTGRES_URI"))

engine = create_engine(database_connection_url(), pool_pre_ping=True)