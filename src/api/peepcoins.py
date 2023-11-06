import sqlalchemy
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


@router.put("/add")
def put_add_peepcoins(request: PeepCoinRequest):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO user_peepcoin_ledger (user_id, change)
                VALUES (:user_id, :change)
                """
            ),
            [{"user_id": request.user_id, "change": request.change}],
        )
    return "OK"
