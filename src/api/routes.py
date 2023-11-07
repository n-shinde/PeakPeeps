import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/routes",
    tags=["routes"],
    dependencies=[Depends(auth.get_api_key)],
)

class Routes(BaseModel):
    name: str
    user_id: int   # id of user that added route
    location: str
    coordinates: list[float]
    length: float
    difficulty: int
    activities: str


@router.post("/add")
def post_add_route(route_to_add: Routes):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO route (name, user_id, location, 
                length_in_miles, difficulty, activities, coords)
                VALUES (:name, :user_id, :location, :length_in_miles,
                :difficulty, :activities, :coords)
                """
            ), [{"name":route_to_add.name, 
                 "user_id":route_to_add.user_id,
                 "location":route_to_add.location,
                 "length_in_miles":route_to_add.length,
                 "difficulty":route_to_add.difficulty,
                 "activities":route_to_add.activities,
                 "coords":route_to_add.coordinates}]
        )
    
    return "OK"

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



@router.get("/friends")
def get_friends_routes(friend_username: Str):
    with db.engine.begin() as connection:
        friend_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT friend_id
                FROM friendship
                JOIN user ON user.Id = friendship.friend_id
                WHERE user.username = :username
                """
            ),[{":username"=friend_username}]).scalars()
        friends = connection.execute(
            sqlalchemy.text(
                """
                SELECT name, date_added, location, length_in_miles,difficulty, activities, coords
                FROM route
                JOIN route ON route.user_id = :friend_id
                """
            ),[{":friend_id"=friend_id}]).scalars()
	
	route_list = []

	for item in friends:
		route_list.append(item)
    
    return route_list
        
    

