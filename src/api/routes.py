import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.api.peepcoins import add_peepcoins
from src.api.users import get_id_from_username
from typing import Optional

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    dependencies=[Depends(auth.get_api_key)],
)


def get_id_from_route_name(route_name, connection):
    return connection.execute(
        sqlalchemy.text(
            """
                SELECT id
                FROM routes
                WHERE name = :name
                """
        ),
        {"name": route_name},
    ).scalar()


class Route(BaseModel):
    name: str
    username: str  # username of user that added route
    coordinates: list[float]
    address: Optional[str]
    length: float  # in miles
    city: Optional[str]
    state: Optional[str]


@router.post("/add")
def post_add_route(route_to_add: Route):
    with db.engine.begin() as connection:
        user_id = get_id_from_username(route_to_add.username, connection)
        new_id = connection.execute(
            sqlalchemy.text(
                """
				INSERT INTO routes (name, added_by_user_id, address, 
				city, state, length_in_miles, coordinates)
				VALUES (:name, :added_by_user_id, :address, :city,
				:state, :length, :coordinates)
                RETURNING id
				"""
            ),
            [
                {
                    "name": route_to_add.name,
                    "added_by_user_id": user_id,
                    "address": route_to_add.address,
                    "length": route_to_add.length,
                    "coordinates": route_to_add.coordinates,
                    "state": route_to_add.state,
                    "city": route_to_add.city,
                }
            ],
        ).scalar_one()

        PEEP_COINS_FROM_ADDING_ROUTE = 10
        add_peepcoins(user_id, PEEP_COINS_FROM_ADDING_ROUTE, connection)
        return new_id


@router.get("/popular")
def get_popular_routes():
    with db.engine.begin() as connection:
        popular_routes = connection.execute(
            sqlalchemy.text(
                """
				SELECT name, date_added, location, length_in_miles,difficulty, activities, coords
				FROM route
				JOIN review ON route.id = review.route_id
				WHERE review.rating >= 4
				"""
            )
        ).scalars()

    route_list = []
    for item in popular_routes:
        route_list.append(item)

    return route_list


@router.get("/followers")
def get_followers_routes(friend_username: str):
    with db.engine.begin() as connection:
        friend_id = connection.execute(
            sqlalchemy.text(
                """
				SELECT follower_id
				FROM followers
				JOIN user_test ON user_test.id = followers.follower_id
				WHERE user_test.username = :username
				"""
            ),
            {"username": friend_username},
        ).scalars()
        friends = connection.execute(
            sqlalchemy.text(
                """
				SELECT name, date_added, location, length_in_miles,difficulty, activities, coords
				FROM route
				WHERE user_id = :friend_id
				"""
            ),
            {"friend_id": friend_id},
        ).scalars()

    route_list = []
    for item in friends:
        route_list.append(item)

    return route_list


@router.post("/report")
def report_route(route_name: str):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE routes
                SET reported = True
                WHERE routes.name = :name
                """
            ),
            {"location": route_name},
        )

    status = "Reported"
    success = True
    return {"report_status": status, "flagged": success}
