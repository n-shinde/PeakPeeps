import pytest
from src.api.admin import reset
from src import database as db
from sqlalchemy import text
from src.api import users
from src.api import routes


@pytest.fixture
def test_data():
    reset()
    with db.engine.begin() as connection:
        queries = []
        queries.append("INSERT INTO users (username) VALUES ('Bob')")
        queries.append(
            "INSERT INTO business (name, address, commissions_rate) VALUES ('Fired and Loaded', '13 Santa Rosa St, San Luis Obispo, CA 93405', 0.9"
        )
        queries.append("")
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
