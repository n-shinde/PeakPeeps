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
    # id: str
    username: str
    # num_followers: int
    # banned: bool


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
        user_update_id = get_id_from_username(user_to_update.username)
        follower_to_add_id = get_id_from_username(follower_to_add.username)

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


@router.post("/follow")
def user_follows_other_user(user_requesting_follow: Users, other_user: Users):
    with db.engine.begin() as connection:
        # Get the user requesting follow id
        user_requesting_follow_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM user_test
                WHERE username = :name
                """
            ),
            {"name": user_requesting_follow.username},
        ).scalar()

        # Get the other user id
        other_user_id = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM user_test
                WHERE username = :name
                """
            ),
            {"name": other_user.username},
        ).scalar()

        # First add new follower to the other user's table
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO followers (id, follower_id)
                VALUES (:other_id, :follower_id)
                """
            ),
            {"other_id": other_user_id, "follower_id": user_requesting_follow_id},
        )

        # Increment other user's followers by 1
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE user_test
                SET num_followers = num_followers + 1
                WHERE id = (
                    SELECT id
                    FROM user_test
                    WHERE username = :name
                )
            """
            ),
            {"name": other_user.username},
        )

    return "OK"


@router.post("/remove_follower")
def remove_follower(user_to_update: Users, follower_to_remove: Users):
    with db.engine.begin() as connection:
        # Retrieve id of person to remove
        follower_to_remove_id = connection.execute(
            sqlalchemy.text(
                """
			SELECT id 
            FROM user_test
            WHERE username = :follower_name
			"""
            ),
            {"follower_name": follower_to_remove.username},
        ).scalar()

        # Find them in followers table and remove
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM followers
                WHERE (id = (SELECT id FROM user_test WHERE username = :name)) and (follower_id = :remove_id)
                """
            ),
            {"name": user_to_update.username, "remove_id": follower_to_remove_id},
        )

        # Decrement user follower list by 1
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE user_test
                SET num_followers = num_followers - 1
                WHERE id = (
                    SELECT id
                    FROM user_test
                    WHERE username = :name
                )
                """
            ),
            {"name": user_to_update.username},
        )
    return "OK"
