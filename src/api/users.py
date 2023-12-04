import sqlalchemy
import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.database import get_id_from_username
from src.api.peepcoins import add_peepcoins_query

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)


@db.handle_errors
@router.post("/create_account")
def post_create_account(username: str):
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text("INSERT INTO users (username) VALUES (:name) RETURNING id"),
            {"name": username},
        ).scalar_one()

        return new_id


@db.handle_errors
@router.get("/{username}")
def get_user(username: str):
    with db.engine.begin() as connection:
        query = sqlalchemy.text(
            "SELECT id, username, num_followers FROM users where username = :username"
        )
        result = connection.execute(query, {"username": username}).one()
        return result._asdict()


@db.handle_errors
@router.post("/add_follower")
def update_followers(user_to_update: str, follower_to_add: str):
    with db.engine.begin() as connection:
        # Get the user to update id
        user_update_id = get_id_from_username(user_to_update, connection)
        follower_to_add_id = get_id_from_username(follower_to_add, connection)

        # First add new follower to followers table
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO followers (user_id, follower_id)
                VALUES (:id, :follower_id)
                """
            ),
            {"id": user_update_id, "follower_id": follower_to_add_id},
        )

        # Increment user's num followers by 1
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE users 
                SET num_followers = num_followers + 1
                WHERE id = :id
                """
            ),
            {"id": user_update_id},
        )

    return "OK"


@db.handle_errors
@router.post("/remove_follower")
def remove_follower(user_to_update: str, follower_to_remove: str):
    with db.engine.begin() as connection:
        follower_to_remove_id = get_id_from_username(follower_to_remove, connection)
        user_to_update_id = get_id_from_username(user_to_update, connection)

        # Find them in followers table and remove
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM followers
                WHERE (user_id = :user_to_update_id) and (follower_id = :remove_id)
                """
            ),
            {
                "user_to_update_id": user_to_update_id,
                "remove_id": follower_to_remove_id,
            },
        )

        # Decrement user follower list by 1
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE users
                SET num_followers = num_followers - 1
                WHERE id = :user_to_update_id
                """
            ),
            {"user_to_update_id": user_to_update_id},
        )
    return "OK"
