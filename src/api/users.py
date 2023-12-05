import sqlalchemy
import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.database import get_id_from_username
#from src.api.peepcoins import add_peepcoins_query

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)
 
 
@db.handle_errors
@router.post("/create_account")
def post_create_account(username: str):
    with db.engine.begin() as connection:
        user_id = get_id_from_username(username, connection)
        
        if user_id is not None:
            raise HTTPException(status_code=404, detail="User already exists")

        new_id = connection.execute(
            sqlalchemy.text("INSERT INTO users (username) VALUES (:name) RETURNING id"),
            {"name": username},
        ).scalar_one()

        return f"User id: {new_id}"


@db.handle_errors
@router.get("/{username}")
def get_user(username: str):
    with db.engine.begin() as connection:
        user_id = get_id_from_username(username, connection)
        if user_id is None:
            raise HTTPException(status_code=404, detail="User does not exists")
            
        result = connection.execute(
            sqlalchemy.text(
            """
            SELECT id, username, num_followers 
            FROM users 
            WHERE username = :username
            """
        ),{"username": username}
        ).fetchall()

        user_info = {
            "id": result[0],
            "username": result[1],
            "num_followers": result[2]   
        }
        return user_info


@db.handle_errors
@router.post("/add_follower")
def update_followers(user_to_update: str, follower_to_add: str):
    """
    user_to_update: the user making the request
    follower_to_add: the person that the user wants to follow

    This endpoint adds the user and the follower to the followers table.
    """
    with db.engine.begin() as connection:
        # Get the user to update id
        user_update_id = get_id_from_username(user_to_update, connection)
        follower_to_add_id = get_id_from_username(follower_to_add, connection)

        if user_update_id is None:
            raise HTTPException(status_code=404, detail="User does not exist")
        if follower_to_add_id is None:
            raise HTTPException(status_code=404, detail="Follower does not exist")
    
        # Make sure they dont already follow each other
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id, follower_id
                FROM followers
                WHERE user_id = :user_id AND follower_id = :follower_id
                """
            ),
            {"user_id": user_update_id, "follower_id": follower_to_add_id},
        ).scalar()

        if exists:
            raise HTTPException(status_code=404, detail="User already following other user")

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
                WHERE id = :follower_id
                """
            ),
            {"follower_id": follower_to_add_id},
        )

    return "OK"


@db.handle_errors
@router.get("/get_following/{username}")
def get_following(username: str):
    """
    Get the list of users whom the specified user is following.

    Parameters:
    - `username` (str): The username of the user to retrieve following list for.

    Returns:
    - List[str]: A list of usernames representing the users being followed by the specified user.
    """

    with db.engine.begin() as connection:
        user_id = get_id_from_username(username, connection)
        
        if user_id is None:
            raise HTTPException(status_code=404, detail="User does not exist")

        result = connection.execute(
            sqlalchemy.text(
                """
        	    SELECT username
        		FROM users
                JOIN followers ON followers.follower_id = users.id
        		WHERE followers.user_id = :user_id
          		"""
            ),
            {"user_id": user_id},
        )

        following_list = [row[0] for row in result.fetchall()]

    return following_list


@db.handle_errors
@router.post("/remove_follower")
def remove_follower(user_to_update: str, follower_to_remove: str):
    with db.engine.begin() as connection:
        follower_to_remove_id = get_id_from_username(follower_to_remove, connection)
        user_to_update_id = get_id_from_username(user_to_update, connection)
        
        if user_to_update_id is None:
            raise HTTPException(status_code=404, detail="User does not exist")
        if follower_to_remove_id is None:
            raise HTTPException(status_code=404, detail="Follower does not exist")


        # Make sure actually follow each other
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id, follower_id
                FROM followers
                WHERE user_id = :user_id AND follower_id = :follower_id
                """
            ),
            {"user_id": user_to_update_id, "follower_id": follower_to_remove_id},
        ).scalar()

        if not exists:
            raise HTTPException(status_code=404, detail="User isn't following other user")


        # Find them in followers table and remove
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM followers
                WHERE (user_id = :user_to_update_id) AND (follower_id = :remove_id)
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
