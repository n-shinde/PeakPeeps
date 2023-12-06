import time
from src.api import businesses
from src.api.admin import reset
from src import database as db
from sqlalchemy import text, true
from src.api.businesses import list_businesses
from src.api.server import app
from src.api import users
from src.api import routes
from src.api import peepcoins
from src.api import coupons
from src.api import reviews
from src.api.auth import get_api_key
import pprint


def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"It tooks {end-start} to run")
        return result

    return wrapper


result = time_it(businesses.list_businesses)()
# print(result)
