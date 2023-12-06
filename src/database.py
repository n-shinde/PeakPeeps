import os
import dotenv
import sqlalchemy
import sqlalchemy.exc
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


### Error Handling Section ###
class FailedLookup(Exception):
    def __init__(self, message="Failed to look up id"):
        self.message = message
        super().__init__(self.message)


def get_id_from_username(username, connection):
    try:
        return connection.execute(
            sqlalchemy.text(
                """
                    SELECT id
                    FROM users
                    WHERE username ILIKE :name
                    """
            ),
            {"name": username},
        ).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        return None
    
def get_id_from_business(business_name, connection):
    try:
        return connection.execute(
            sqlalchemy.text(
                """
                    SELECT id
                    FROM business
                    WHERE name ILIKE :name
                    """
            ),
            {"name": business_name},
        ).scalar_one()
    
    except sqlalchemy.exc.NoResultFound:
        return None
    
def get_id_from_coupons(coupon_name, connection):
    try:
        return connection.execute(
            sqlalchemy.text(
                """
                    SELECT id
                    FROM coupons
                    WHERE name ILIKE :name
                    """
            ),
            {"name": coupon_name},
        ).scalar_one()
    
    except sqlalchemy.exc.NoResultFound:
        return None


# Doing some magic with decorators. Check out this 60-second video look behind the curtain
# https://www.youtube.com/watch?v=BE-L7xu8pO4
# But basically, if we decorate our functions with this, we can do all the general error handling here,
# So we don't have to do it to every function individually
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FailedLookup as e:
            return e.message
        except sqlalchemy.exc.NoResultFound as e:
            return e

    return wrapper
