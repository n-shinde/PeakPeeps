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
    id: int 
    username: str
    #date_joined: str
    #num_followers: int
    #banned: bool

@router.post("/create_account")
def post_create_account(user_created: Users):

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
				INSERT INTO user (username)
				VALUES (:name)
				"""
            ), [{"name": user_created.username}]
        )

@router.post("/add_follower")
def update_followers(user_to_update: Users, follower_to_add: Users):

    with db.engine.begin() as connection:
        isBanned = connection.execute(
            sqlalchemy.text(
                """
				SELECT banned 
                FROM user
                WHERE id = :follow_id
				"""
            ), [{"follow_id": follower_to_add.id}]
        ).scalar()

    if (isBanned == False):
        with db.engine.begin() as connection:
            # First add new follower to followers table
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO followers (id, follower_id)
                    VALUES (:id, :follower_id)
                    """
                ), [{"id": user_to_update.id, "follower_id": follower_to_add.id}]
            )

            # Increment user's num followers by 1
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE user 
                    SET num_followers += 1
                    WHERE id = :id
                    """
                ), [{"id": user_to_update.id}]
            )

    else:
        return "User banned. Cannot follow this user."



@router.post("/follow")
def user_follows_other_user(user_requesting_follow: Users, other_user: Users):

    with db.engine.begin() as connection:
        isBanned = connection.execute(
            sqlalchemy.text(
                """
				SELECT banned 
                FROM user
                WHERE id = :other_id
				"""
            ), [{"other_id": other_user.id}]
        ).scalar()
    
    if (isBanned == False):
       with db.engine.begin() as connection:
            # First add new follower to the other user's table
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO followers (id, follower_id)
                    VALUES (:other_id, :follower_id)
                    """
                ), [{"id": other_user.id, "follower_id": user_requesting_follow.id}]
            )

            # Increment other user's followers by 1
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE user
                    SET num_followers += 1
                    WHERE id = :other_id
                    """
                ), [{"other_id": other_user.id}]
            )

    else:
       return "User you are trying to follow is banned."

@router.post("/remove_follower")
def remove_follower(user_id: int, follower_to_remove: str):

    with db.engine.begin() as connection:
        # Retrieve id of person to remove
        follower_to_remove_id = connection.execute(
            sqlalchemy.text(
                """
				SELECT id 
                FROM user
                WHERE username = :follower_name
				"""
            ), [{"follower_name": follower_to_remove}]
        ).scalar()
    
        # Find them in followers table and remove
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM followers
                WHERE (user_id = :user_id) and (follower_id = :remove_id)
                """
            ), [{"user_id": user_id, "remove_id": follower_to_remove_id}]
        )

        # Decrement user follower list by 1
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE user
                SET num_followers -= 1
                WHERE id = :user_id
                """
            ), [{"other_id": user_id}]
        )





       
    






