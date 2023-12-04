import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.api.peepcoins import add_peepcoins
from src.api.users import get_id_from_username
from typing import Optional
from enum import Enum

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    dependencies=[Depends(auth.get_api_key)],
)


class search_sort_options(str, Enum):
    route_name = "route_name"
    length_miles = "length_miles"
    city = "city"


class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"


@db.handle_errors
@router.get("/search/")
def search_orders(
    route_name: str = "",
    user_added: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.route_name,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for routes items by route_name and/or potion.

    Route name and user sku filter to orders that contain the
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku,
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    sort_by_col = "name"

    sort_by_order = "desc"

    if sort_col == search_sort_options.length_miles:
        sort_by_col = "length_in_miles"

    elif sort_col == search_sort_options.city:
        sort_by_col = "city"

    if sort_order == search_sort_order.asc:
        sort_by_order = "asc"

    page_size = 5

    # Determine the offset based on the search_page token

    if search_page == "":
        offset = 0

    else:
        offset = int(search_page)

    # Not negative
    if offset - 5 >= 0:
        prev_page = str(offset - 5)

    else:
        prev_page = ""

    with db.engine.begin() as connection:
        result_len = connection.execute(
            sqlalchemy.text(
                f"""
                SELECT COUNT(*)
                FROM
                routes
                JOIN users ON 
                    users.id = routes.added_by_user_id
                """
            )
        )

    len_of_data = result_len.scalar()
    print(len_of_data)

    query = f"""
                SELECT
                routes.name AS name,
                routes.length_in_miles AS length_miles,
                routes.city AS city,
                routes.added_by_user_id AS user

                FROM routes

                JOIN users ON 
                    users.id = routes.added_by_user_id

                AND routes.name ILIKE '%{route_name}%'
                AND routes.name ILIKE '%{user_added}%'
                ORDER BY
                {sort_by_col} {sort_by_order}
                LIMIT {page_size}
                OFFSET {offset};

                """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(query))

    # Fetch all rows from the result
    data = result.fetchall()
    lst = []

    print(data)
    print(len(data))

    # Not negative
    if offset + 5 > len(data):
        next_page = ""

    else:
        next_page = str(offset + 5)

    for row in data:
        print(row.name)
        print(row.length_miles)
        print(row.city)
        print(row.user)

        lst.append(
            {
                "route_name": row.name,
                "length_miles": row.length_miles,
                "city": row.city,
                "user": row.user,
            }
        )

    return {"previous": prev_page, "next": next_page, "results": lst}


@db.handle_errors
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


@db.handle_errors
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


@db.handle_errors
@router.get("/popular")
def get_popular_routes():
    with db.engine.begin() as connection:
        popular_routes = connection.execute(
            sqlalchemy.text(
                """
		SELECT name, date_added, location, length_in_miles,difficulty, activities, coords, AVG(review.rating) AS Rating
		FROM route
		JOIN review ON route.id = review.route_id
  		GROUP BY name
		HAVING Rating >= 4 AND COUNT(review.rating) > 5
  		ORDER BY Rating DESC
  		LIMIT 10
		"""
            )
        ).scalars()

    route_list = []
    for item in popular_routes:
        route_list.append(item)

    return route_list


@db.handle_errors
@router.get("/followers")
def get_followers_routes(friend_username: str, username: str):
    with db.engine.begin() as connection:
        friend_id = get_id_from_username(friend_username, connection)
        user_id = get_id_from_username(username, connection)

        friend_check = connection.execute(
            sqlalchemy.text(
                """
                SELECT A.follower_id AS user1, A.user_id AS user2
            FROM followers A
            JOIN followers B ON A.follower_id = B.user_id AND A.user_id = B.follower_id
            WHERE A.follower_id = :follower_id AND A.user_id = :user_id
            """
            ),
            {"follower_id": friend_id, "user_id": user_id},
        )
        if not friend_check.fetchone():
            "User isn't friends with other user, cannot retrieve routes."

            friends = connection.execute(
                sqlalchemy.text(
                    """
            SELECT name, date_added, location, length_in_miles,difficulty, activities, coords, AVG(review.rating) AS Rating
            FROM route
            WHERE user_id = :friend_id
                GROUP BY name
            HAVING Rating >= 4 AND COUNT(review.rating) > 5
            ORDER BY Rating DESC
            LIMIT 10
            """
                ),
                {"friend_id": friend_id},
            ).scalars()

            route_list = []
            for item in friends:
                route_list.append(item)

            return route_list


@db.handle_errors
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
            {"name": route_name},
        )

    status = "Reported"
    success = True
    return {"report_status": status, "flagged": success}


@db.handle_errors
@router.post("/complete")
def complete_route(route_name: str, username: str):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE routes
                SET num_completed = num_completed + 1
                WHERE routes.name = :name
                """
            ),
            {"name": route_name},
        )

        user_id = get_id_from_username(username, connection)
        PEEP_COINS_FROM_COMPLETING_ROUTE = 15
        add_peepcoins(user_id, PEEP_COINS_FROM_COMPLETING_ROUTE, connection)

        return {"OK"}
