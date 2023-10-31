import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    dependencies=[Depends(auth.get_api_key)],
)

class Reviews(BaseModel):
    author_name: str
    route_id: int
    description: str
    rating: int # On a scale of 1 - 5 (only ints)

@router.post("/add")
def post_add_review(review_to_add: Reviews):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO review (route_id, author_name, description, rating)
                VALUES (:route_id, :author_name, :description, :rating)
                """
            ), [{"route_id":review_to_add.route_id,
                "author_name":review_to_add.author_name, 
                 "description":review_to_add.description,
                 "rating":review_to_add.rating}]
        )
    
    return "OK"
