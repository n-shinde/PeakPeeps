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
    location: str
    description: str
    rating: int # On a scale of 1 - 5 (only ints)

@router.post("/add")
def post_add_review(review_to_add: Reviews):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO review (author_name, location, description, rating)
                VALUES (:author_name, :location, :description, :rating)
                """
            ), [{"author_name":review_to_add.author_name, 
                 "location":review_to_add.location,
                 "description":review_to_add.description,
                 "rating":review_to_add.rating}]
        )
    
    return "OK"

# @router.post("/get")
# def get_reviews(review_catalog: list[Reviews]):
