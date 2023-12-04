from codecs import backslashreplace_errors
from sqlite3 import connect
import pytest
from fastapi.testclient import TestClient
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Request
import os
import dotenv
import sqlalchemy
from src.api import businesses

from src.api.admin import reset
from src import database as db
from sqlalchemy import text
from src.api.businesses import list_businesses
from src.api.server import app
from src.api import users
from src.api import routes
from src.api import peepcoins
from src.api import coupons
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
    dotenv.load_dotenv()
    deployment_type = os.environ.get("DEPLOYMENT_TYPE")
    if deployment_type != "development":
        raise Exception(
            f"Deployment type in the env must be development, got {deployment_type}"
        )

    reset()
    with db.engine.begin() as connection:
        queries = []
        queries.append("INSERT INTO users (id, username) VALUES (1, 'Bob')")
        queries.append("INSERT INTO users (id, username) VALUES (2, 'Alice')")
        queries.append("INSERT INTO users (id, username) VALUES (3, 'Eve')")
        queries.append(
            "INSERT INTO business (id, name, address, commissions_rate) VALUES (1, 'Fried and Loaded', '13 Santa Rosa St, San Luis Obispo, CA 93405', 0.9)"
        )
        queries.append(
            "INSERT INTO business (id, name, address, commissions_rate) VALUES (2, 'SQL Tea', '3845 S Higuera St Ste 100, San Luis Obispo, CA 93401', 0.95)"
        )
        queries.append(
            "INSERT INTO coupons (id, name, valid, business_id, price) VALUES (1, 'Half off Smashburger', True, 1, 25)"
        )
        queries.append(
            "INSERT INTO coupons (id, name, valid, business_id, price) VALUES (2, 'BOGO Milk Shakes', False, 1, 10)"
        )
        queries.append(
            "INSERT INTO coupons (id, name, valid, business_id, price) VALUES (3, 'An Invalid coupon', False, 2, 5)"
        )
        queries.append(
            """INSERT INTO routes (id, name, address, city, state, length_in_miles, added_by_user_id, coordinates, reported)
            VALUES (1, 'Bishop Peak', 'Patricia Drive', 'San Luis Obispo', 'CA', 3.7, 1, ARRAY[35.30327857570746, -120.69743771424115], FALSE)"""
        )
        queries.append(
            """INSERT INTO routes (id, name, address, city, state, length_in_miles, added_by_user_id, coordinates, reported)
            VALUES (2, 'Resevoir Canyon Loop', 'Resevoir canyon natural reserve', 'San Luis Obispo', 'CA', 5.5, 2, ARRAY[35.30327857570746, -120.69743771424115], FALSE)"""
        )
        queries.append(
            """INSERT INTO routes (id, name, address, city, state, length_in_miles, added_by_user_id, coordinates, reported)
            VALUES (3, 'Lemon Grove and rock garden loop', 'Lemon GRove', 'San Luis Obispo', 'CA', 4.1, 3, ARRAY[35.30327857570746, -120.69743771424115], FALSE),
            (4, 'Felsman Loop', 'Ferrini Ranch', 'San Luis Obispo', 'CA', 4.1, 3, ARRAY[35.30327857570746, -120.69743771424115], FALSE),
            (5, 'Poly Canyon', 'Peterson Ranch', 'San Luis Obispo', 'CA', 4.6, 1, ARRAY[35.30327857570746, -120.69743771424115], FALSE),
            (6, 'Froom Canyon', 'Irish Hills', 'San Luis Obispo', 'CA', 3.8, 3, ARRAY[35.30327857570746, -120.69743771424115], FALSE),
            (7, 'M Trail', 'Cerro San Luis', 'San Luis Obispo', 'CA', 2.5, 3, ARRAY[35.30327857570746, -120.69743771424115], FALSE),
            (8, 'Johnson Ranch Loop', 'Johnson Ranch', 'San Luis Obispo', 'CA', 4.1, 3, ARRAY[35.30327857570746, -120.69743771424115], FALSE)
            """
        )
        for query in queries:
            connection.execute(text(query))


def test_add_user(test_data):
    # setting up
    new_id = users.post_create_account("Paul")

    with db.engine.begin() as connection:
        user_id = db.handle_errors(users.get_id_from_username)("Paul", connection)
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
        coupons.buy_coupon(1, 1, connection)
        query = "select sum(change) from user_coupon_ledger WHERE user_id = 1 and coupon_id = 1"
        coupon_result = connection.execute(text(query)).scalar_one()
        assert coupon_result == 1

        query = "select sum(change) from user_peepcoin_ledger where user_id = 1"
        balance = connection.execute(text(query)).scalar_one()
        assert balance == 5


def test_buy_coupon_no_money(test_data):
    with db.engine.begin() as connection:
        query = text("INSERT INTO user_peepcoin_ledger (user_id, change) VALUES (1, 5)")
        connection.execute(query)
        connection.commit()

    request = coupons.CouponRequest(coupon_id=1, user_id=1)
    result = coupons.post_buy_coupon(request)
    assert result == "user can't afford coupon"


def test_buy_invalid_coupon(test_data):
    request = coupons.CouponRequest(coupon_id=2, user_id=1)
    result = coupons.post_buy_coupon(request)
    assert result == "coupon not valid"


def test_edit_coupon(test_data):
    request = coupons.EditCouponRequest(
        business_id=1,
        coupon_name="Half off Smashburger",
        price=50,
        new_coupon_name=None,
        is_valid=None,
    )

    result = coupons.edit_coupon(request)
    assert result == "OK"


def test_get_coupon(test_data):
    request = coupons.GetCouponRequest(
        business_id=1, coupon_name="Half off Smashburger"
    )
    result = coupons.get_coupon(request)
    assert result.price == 25
    assert result.valid == True


def test_list_businesses(test_data):
    request = businesses.ListBusinessesRequest(should_have_valid_coupon=True)
    result = list_businesses(request)
    assert [
        {
            "address": "13 Santa Rosa St, San Luis Obispo, CA 93405",
            "id": 1,
            "name": "Fried and Loaded",
        }
    ] == result


def test_update_followers(test_data):
    users.update_followers("Alice", "Eve")
    users.update_followers("Alice", "Bob")
    users.update_followers("Bob", "Eve")

    alice = users.get_user("Alice")
    bob = users.get_user("Bob")
    assert alice["num_followers"] == 2
    assert bob["num_followers"] == 1


def test_remove_followers(test_data):
    users.update_followers("Alice", "Eve")
    users.remove_follower("Alice", "Eve")
    alice = users.get_user("Alice")
    assert alice["num_followers"] == 0


def test_update_followers_non_existsant(test_data):
    result = users.update_followers("Gwen", "Eve")
    assert result == "can't find user Gwen"


def test_update_followers_non_existsant_2(test_data):
    result = users.update_followers("Eve", "Gwen")
    assert result == "can't find user Gwen"


def test_report_route(test_data):
    routes.report_route("Bishop Peak")
    with db.engine.begin() as connection:
        query = text("SELECT * FROM routes WHERE name = 'Bishop Peak'")
        result = connection.execute(query).one()
        assert result.reported == True


def test_report_route_nonexistant(test_data):
    result = routes.report_route("I don't exists")
    assert result == "Can't find 'I don't exist'"
    # doesn't have to be this result exactlty,
    # but we should have some error message that the lookup failed


def test_search_route_name(test_data):
    result = routes.search_routes(route_name="Peak")
    assert {
        "next": "",
        "previous": "",
        "results": [
            {
                "city": "San Luis Obispo",
                "length_miles": 3.7,
                "route_name": "Bishop Peak",
                "user": 1,
            }
        ],
    } == result


def test_search_route_user(test_data):
    result = routes.search_routes(user_added="Bob")
    assert {
        "next": "",
        "previous": "",
        "results": [
            {
                "city": "San Luis Obispo",
                "length_miles": 3.7,
                "route_name": "Bishop Peak",
                "user": 1,
            }
        ],
    } == result


def test_search_routes_multiple_pages(test_data):
    result = routes.search_routes(search_page=1)
    assert len(result) == 5
    assert result == "foo"


def test_get_followers_routes(test_data):
    users.update_followers("Eve", "Bob")
    result = routes.get_followers_routes("Bob", "Eve")
    assert result == "foo"
