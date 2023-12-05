from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.api.users import get_username
from src.api.users import get_id_from_username

router = APIRouter(
    prefix="/peepcoins",
    tags=["peepcoins"],
    dependencies=[Depends(auth.get_api_key)],
)


class PeepCoinRequest(BaseModel):
    user_id: int
    change: int


add_peepcoins_query = text(
    """
    INSERT INTO user_peepcoin_ledger (user_id, change)
    VALUES (:user_id, :change)
    """
)


@db.handle_errors
def add_peepcoins(username, amount, connection):
    user_id = get_id_from_username(username, connection)

    query = text(
        """
        INSERT INTO user_peepcoin_ledger (user_id, change)
        VALUES (:user_id, :change)
        """
    )
    connection.execute(query, {"user_id": user_id, "change": amount})


@db.handle_errors
@router.put("/add")
def put_add_peepcoins(request: PeepCoinRequest):
    with db.engine.begin() as connection:
        add_peepcoins(request.user_id, request.change, connection)
    return "OK"

@db.handle_errors
@router.get("/get")
def get_peepcoins(username: str):

    with db.engine.begin() as connection:
        user_id = get_id_from_username(username, connection)

        query = text(
        """
        SELECT SUM(change)
        FROM user_peepcoin_ledger
        WHERE user_id = :user_id
        """
        )

        result = connection.execute(query, {"user_id": user_id})

        if not result:
            return f"failed to look up peepcoins for user: {username}"
