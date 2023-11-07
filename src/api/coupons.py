from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db


router = APIRouter(
    prefix="/coupons",
    tags=["coupons"],
    dependencies=[Depends(auth.get_api_key)],
)


class Coupons(BaseModel):
    business_id: int
    name: str
    cost: int


@router.put("/add")
def add_coupon(request: Coupons):
    with db.engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO coupons (business_id, name, cost)
                VALUES (:bus_id, :name, :cost)
                """
            ),
            [
                {
                    "bus_id": request.business_id,
                    "name": request.name,
                    "cost": request.cost,
                }
            ],
        )
    return "OK"
