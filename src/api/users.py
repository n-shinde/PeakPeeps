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
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT (user_id)
                FROM users
                WHERE username = :username
                """
            ),{"name": username}
        ).scalars()

        if exists.fetchone():
            return "Username already taken. Please pick another username."


        new_id = connection.execute(
            sqlalchemy.text("INSERT INTO users (username) VALUES (:name) RETURNING id"),
            {"name": username},
        ).scalar_one()

        return f"User id: {new_id}"


@db.handle_errors
@router.get("/{username}")
def get_user(username: str):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
            """
            SELECT id, username, num_followers 
            FROM users 
            WHERE username = :username
            """
        ),{"username": username}
        ).scalar_one()

        if not result.fetchone():
            return "This user does not exist"

        return result._asdict()
    
@db.handle_errors
@router.get("/{user_id}")
def get_username(user_id: int):
    with db.engine.begin() as connection:
        query = sqlalchemy.text(
            "SELECT username FROM users where id = :user_id"
        )
        result = connection.execute(query, {"user_id": user_id}).scalar_one()
        return result


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

        # Edge condition to make sure user exists
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT username
                FROM users
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_update_id},
        ).scalar()

        if not exists.fetchone():
            return "Username doesn't exist"

        # Make sure requested follower exists
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT username
                FROM users
                WHERE user_id = :user_id
                """
            ),
            {"user_id": follower_to_add_id},
        ).scalar()

        if exists.fetchone():
            return "Follower username doesn't exist"

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

        if exists.fetchone():
            return "User already following other user"

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
@router.get("/get_following")
def get_following(username: str):
    """
    This endpoint returns all of the friends of a certain user. The qualifications of a "friend" means that
    both users follow each other. There will be two rows in the follower table to represent this relationship.
    """
    with db.engine.begin() as connection:
        user_id = get_id_from_username(username, connection)



        get_following = connection.execute(
            sqlalchemy.text(
                """
        	    SELECT username
        		FROM users
                JOIN followers ON followers.follower_id = users.user_id
        		WHERE followers.user_id = :user_id
          		"""
            ),
            {"user_id": user_id},
        ).scalars()

        
        # friends = []
        # for item in get_following:
        #     get_friend = connection.execute(
        #         sqlalchemy.text(
        #             """
        #     	    SELECT username
        #     		FROM users
        #             JOIN followers ON users.user_id = followers.follower_id
        #     		WHERE follower_id = :user_id AND user_id = :follower_id
        #       		"""
        #         ),
        #         {"follower_id": item.follower_id, "user_id": user_id},
        #     )

        #     if get_friend.fetchone():
        #         friends.append(get_friend.first())

    return list(get_following)


@db.handle_errors
@router.post("/remove_follower")
def remove_follower(user_to_update: str, follower_to_remove: str):
    with db.engine.begin() as connection:
        follower_to_remove_id = get_id_from_username(follower_to_remove, connection)
        user_to_update_id = get_id_from_username(user_to_update, connection)

        # Edge condition to make sure user exists
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT username
                FROM users
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_update_id},
        ).scalar()

        if not exists.fetchone():
            return "Username doesn't exist"

        # Make sure requested follower exists
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT username
                FROM users
                WHERE user_id = :user_id
                """
            ),
            {"user_id": follower_to_add_id},
        ).scalar()

        if exists.fetchone():
            return "Follower username doesn't exist"

        # Make sure actually follow each other
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

        if not exists.fetchone():
            return "User isn't following other user"


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
