import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy import text
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
    route_name: str
    description: str
    rating: int  # On a scale of 1 - 5 (only ints)
    difficulty: int  # on a scale of 1-5


@db.handle_errors
@router.post("/add")
def post_add_review(review_to_add: Reviews):
    """
    review_to_add: a Reviews class object
    This endpoint adds a review to a certain route, given the route_name and username.
    A user can only add one review to each route (to prohibit spamming of reviews for peepcoins).
    If a review has already been submitted by the user, and error message is returned.
    """
    with db.engine.begin() as connection:
        # Check that user and route id's are valid
        user_id = get_id_from_username(review_to_add.username, connection)
        route_id = get_id_from_route_name(review_to_add.route_name, connection)

        if not user_id:
            raise HTTPException(status_code=404, detail="User does not exist")
        
        if not route_id:
            raise HTTPException(status_code=404, detail="Route does not exist")
        
        # Check that rating and difficulty are valid 
        if not (isinstance(review_to_add.rating, int) and 1 <= review_to_add.rating <= 5):
            raise HTTPException(status_code=404, detail="Invalid input for rating. Rating must be an integer between 1-5.")
        
        if not (isinstance(review_to_add.difficulty, int) and 1 <= review_to_add.difficulty <= 5):
            raise HTTPException(status_code=404, detail="Invalid input for difficulty. Difficulty must be an integer between 1-5.")

        completed_check = connection.execute(
            sqlalchemy.text(
                """
            SELECT user_id,route_id
            FROM completed_route_ledger
            WHERE user_id = :user_id AND route_id = :route_id
            """
            ),
            {"user_id": user_id, "route_id": route_id},
        )

        if not completed_check.fetchone():
            return "User has not completed this route, cannot submit review."

        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM review
                WHERE user_id = :user_id AND route_id = :route_id
                """
            ),
            {"user_id": user_id, "route_id": route_id},
        )

        if result.fetchone():
            return "User has already submitted a review for this route."

        review_id = connection.execute(
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
        ).scalars()

        PEEP_COINS_FROM_POSTING_REVIEW = 5
        add_peepcoins(review_to_add.username, PEEP_COINS_FROM_POSTING_REVIEW, connection)

    return f"Review ID: {review_id}"

class EditReviewRequest(BaseModel):
    username: str
    route_name: str
    new_description: Optional[str]
    new_rating: Optional[int]
    new_difficulty: Optional[int]


@db.handle_errors
@router.post("/update")
def post_update_review(request: EditReviewRequest):
    """
    Update a user's review for a specific route.

    Parameters:
    - request (EditReviewRequest): An object containing information about the review update,
    including the username, route name, and new review details.

    Returns:
    - str: A confirmation message ("OK") indicating that the review was successfully updated.
    """

    with db.engine.begin() as connection:
        # Get the current review
        user_id = get_id_from_username(request.username, connection)
        route_id = get_id_from_route_name(request.route_name, connection)

        # Check to make sure that review and difficulty are in range
        if not(isinstance(request.new_rating, int) and 1 <= request.new_rating <= 5) and request.new_rating is not None:
            raise HTTPException(status_code=404, detail="Invalid input for rating. Rating must be an integer between 1-5.")
        
        if not(isinstance(request.new_difficulty, int) and 1 <= request.new_difficulty <= 5) and request.new_difficulty is not None:
            raise HTTPException(status_code=404, detail="Invalid input for difficulty. Difficulty must be an integer between 1-5.")

         # Check that user id, route id are valid
        if not user_id:
            raise HTTPException(status_code=404, detail="User does not exist")
        
        if not route_id:
            raise HTTPException(status_code=404, detail="Route does not exist")

        query = """
            SELECT user_id, route_id, description, rating, difficulty
            FROM review 
            WHERE user_id = :user_id AND route_id = :route_id
        """
        current_review = connection.execute(
            text(query),
            {
                "user_id": user_id,
                "route_id": route_id,
            },
        ).first()

        if not current_review:
            raise HTTPException(status_code=404, detail=f"Could not find a review from user {request.username} for route {request.route_name}")
        
        # updating the values of the coupon if they were passed in the request
        description = request.new_description or current_review.description
        rating = request.new_rating or current_review.rating
        difficulty = request.new_difficulty or current_review.difficulty

        query = text(
            """
            UPDATE review SET description = :description, rating = :rating, difficulty = :difficulty
            WHERE route_id = :route_id AND user_id = :user_id
            """
        )
        connection.execute(
            query, {"description": description, "rating": rating, "difficulty": difficulty, "route_id": route_id, "user_id": user_id}
        )
        
        return "OK"
