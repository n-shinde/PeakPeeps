import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.api.peepcoins import add_peepcoins_query

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    dependencies=[Depends(auth.get_api_key)],
)


class Reviews(BaseModel):
    user_id: int
    route_id: int
    description: str
    rating: int  # On a scale of 1 - 5 (only ints)


@router.post("/add")
def post_add_review(review_to_add: Reviews):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO review (route_id, user_id, description, rating)
                VALUES (:route_id, :user_id, :description, :rating)
                """
            ),
            [
                {
                    "route_id": review_to_add.route_id,
                    "user_id": review_to_add.user_id,
                    "description": review_to_add.description,
                    "rating": review_to_add.rating,
                }
            ],
        )

        PEEP_COINS_FROM_POSTING_REVIEW = 5
        connection.execute(
            add_peepcoins_query,
            {
                "user_id": review_to_add.user_id,
                "change": PEEP_COINS_FROM_POSTING_REVIEW,
            },
        )
    return "OK"
