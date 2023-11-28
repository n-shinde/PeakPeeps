import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.api.peepcoins import add_peepcoins_query

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)


class Users(BaseModel):
    username: str


@router.post("/create_account")
def post_create_account(user_created: Users):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("INSERT INTO user_test (username) VALUES (:name)"),
            {"name": user_created.username},
        )

    return "OK"


def get_id_from_username(username, connection):
    return connection.execute(
        sqlalchemy.text(
            """
                SELECT id
                FROM user_test
                WHERE username = :name
                """
        ),
        {"name": username},
    ).scalar()


@router.post("/add_follower")
def update_followers(user_to_update: Users, follower_to_add: Users):
    with db.engine.begin() as connection:
        # Get the user to update id
        user_update_id = get_id_from_username(user_to_update.username, connection)
        follower_to_add_id = get_id_from_username(follower_to_add.username, connection)

        # First add new follower to followers table
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO followers (id, follower_id)
                VALUES (:id, :follower_id)
                """
            ),
            {"id": user_update_id, "follower_id": follower_to_add_id},
        )

        # Increment user's num followers by 1
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE user_test 
                SET num_followers = num_followers + 1
                WHERE id = :id
                """
            ),
            {"id": user_update_id},
        )

    return "OK"


@router.post("/remove_follower")
def remove_follower(user_to_update: Users, follower_to_remove: Users):
    with db.engine.begin() as connection:
        follower_to_remove_id = get_id_from_username(
            follower_to_remove.username, connection
        )
        user_to_update_id = get_id_from_username(user_to_update.username, connection)

        # Find them in followers table and remove
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM followers
                WHERE (id = :user_to_update_id) and (follower_id = :remove_id)
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
                UPDATE user_test
                SET num_followers = num_followers - 1
                WHERE id = :user_to_update_id
                """
            ),
            {"user_to_update_id": user_to_update_id},
        )
    return "OK"
