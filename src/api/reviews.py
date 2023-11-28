import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.api.peepcoins import add_peepcoins
from src.api.users import get_id_from_username
from src.api.routes import get_id_from_route_name

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    dependencies=[Depends(auth.get_api_key)],
)


class Reviews(BaseModel):
    username: str
    route_name: int
    description: str
    rating: int  # On a scale of 1 - 5 (only ints)
    difficulty: int  # on a scale of 1-5


@router.post("/add")
def post_add_review(review_to_add: Reviews):
    with db.engine.begin() as connection:
        user_id = get_id_from_username(review_to_add.username, connection)
        route_id = get_id_from_route_name(review_to_add.route_name, connection)

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO review (route_id, user_id, description, rating, difficulty)
                VALUES (:route_id, :user_id, :description, :rating, :difficulty)
                """
            ),
            [
                {
                    "route_id": route_id,
                    "user_id": user_id,
                    "description": review_to_add.description,
                    "rating": review_to_add.rating,
                    "difficulty": review_to_add.difficulty,
                }
            ],
        )

        PEEP_COINS_FROM_POSTING_REVIEW = 5
        add_peepcoins(user_id, PEEP_COINS_FROM_POSTING_REVIEW, connection)
    return "OK"
