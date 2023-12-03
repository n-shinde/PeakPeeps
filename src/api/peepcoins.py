from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db

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


def add_peepcoins(user_id, amount, connection):
    query = text(
        """
        INSERT INTO user_peepcoin_ledger (user_id, change)
        VALUES (:user_id, :change)
        """
    )
    connection.execute(query, {"user_id": user_id, "change": amount})


@router.put("/add")
def put_add_peepcoins(request: PeepCoinRequest):
    with db.engine.begin() as connection:
        add_peepcoins(request.user_id, request.change, connection)
    return "OK"
