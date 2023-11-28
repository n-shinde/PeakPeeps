from fastapi import APIRouter, Depends, Request
from src.api import auth
from src import database as db
from sqlalchemy import text

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset")
def reset():
    with db.engine.begin() as connection:
        """
        Reset the game state. Gold goes to 100, all potions are removed from
        inventory, and all barrels are removed from inventory. Carts are all reset.
        """

        queries = []
        queries.append(text("TRUNCATE TABLE user_coupon_ledger CASCADE"))
        queries.append(text("TRUNCATE TABLE user_peepcoin_ledger CASCADE"))
        queries.append(text("TRUNCATE TABLE followers CASCADE"))
        queries.append(text("TRUNCATE TABLE review CASCADE"))
        queries.append(text("TRUNCATE TABLE coupons CASCADE"))
        queries.append(text("TRUNCATE TABLE business CASCADE"))
        queries.append(text("TRUNCATE TABLE routes CASCADE"))
        queries.append(text("TRUNCATE TABLE users CASCADE"))

        for query in queries:
            print(query)
            connection.execute(query)
