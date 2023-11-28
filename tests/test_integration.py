from codecs import backslashreplace_errors
from sqlite3 import connect
import pytest
from fastapi.testclient import TestClient
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Request

from src.api.admin import reset
from src import database as db
from sqlalchemy import text
from src.api.server import app
from src.api import users
from src.api import routes
from src.api import peepcoins
from src.api.auth import get_api_key

client = TestClient(app)
api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def get_api_key_override(
    request: Request, api_key_header: str = Security(api_key_header)
):
    return api_key_header


app.dependency_overrides[get_api_key] = get_api_key_override


@pytest.fixture
def test_data():
    reset()
    with db.engine.begin() as connection:
        queries = []
        queries.append("INSERT INTO users (id, username) VALUES (1, 'Bob')")
        queries.append(
            "INSERT INTO business (id, name, address, commissions_rate) VALUES (1, 'Fired and Loaded', '13 Santa Rosa St, San Luis Obispo, CA 93405', 0.9)"
        )
        queries.append(
            "INSERT INTO coupons (id, name, valid, business_id, price) VALUES (1, 'Half off Smashburger', True, 1, 25)"
        )
        queries.append(
            "INSERT INTO coupons (id, name, valid, business_id, price) VALUES (2, 'GOGO Milk Shakes', False, 1, 10)"
        )
        for query in queries:
            connection.execute(text(query))


def test_add_user(test_data):
    # setting up
    request = users.Users(username="Paul")
    new_id = users.post_create_account(request)

    with db.engine.begin() as connection:
        user_id = users.get_id_from_username("Paul", connection)
        assert new_id == user_id


def test_add_route(test_data):
    request = routes.Route(
        name="the p",
        username="Bob",
        coordinates=[0, 50],
        address="water reservoir 1",
        city="san luis obispo",
        state="ca",
        length=2,
    )
    new_id = routes.post_add_route(request)
    with db.engine.begin() as connection:
        route_id = routes.get_id_from_route_name("the p", connection)
        assert new_id == route_id


def test_add_route_without_optional(test_data):
    request = routes.Route(
        name="the p",
        username="Bob",
        coordinates=[0, 50],
        state="ca",
        length=2,
        address=None,
        city=None,
    )
    new_id = routes.post_add_route(request)
    with db.engine.begin() as connection:
        route_id = routes.get_id_from_route_name("the p", connection)
        assert new_id == route_id


def test_buy_coupon(test_data):
    with db.engine.begin() as connection:
        query = text(
            "INSERT INTO user_peepcoin_ledger (user_id, change) VALUES (1, 30)"
        )
        connection.execute(query)
        connection.commit()

    request = {"coupon_id": 1, "user_id": 1}
    client.post("/peepcoins/purchase/coupon", json=request)

    with db.engine.begin() as connection:
        query = "select sum(change) from user_coupon_ledger WHERE user_id = 1 and coupon_id = 1"
        coupons = connection.execute(text(query)).scalar_one()

        query = "select sum(change) from user_peepcoin_ledger where user_id = 1"
        balance = connection.execute(text(query)).scalar_one()
        assert coupons == 1
        assert balance == 5


def test_buy_coupon_no_money(test_data):
    with db.engine.begin() as connection:
        query = text("INSERT INTO user_peepcoin_ledger (user_id, change) VALUES (1, 5)")
        connection.execute(query)
        connection.commit()

    request = peepcoins.CouponRequest(coupon_id=1, user_id=1)
    result = peepcoins.post_buy_coupon(request)
    assert result == "user can't afford coupon"


def test_buy_invalid_coupon(test_data):
    request = peepcoins.CouponRequest(coupon_id=2, user_id=1)
    result = peepcoins.post_buy_coupon(request)
    assert result == "coupon not valid"
