from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
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


class EditCouponRequest(BaseModel):
    business_name: str
    coupon_name: str
    new_coupon_name: Optional[str]
    is_valid: Optional[str]
    price: Optional[int]


@router.post("/edit")
def edit_coupon(request: EditCouponRequest):
    with db.engine.begin() as connection:
        # get the current coupon
        query = """
            Select id, name, valid, price from coupons
                WHERE name = :coupon_name
                    AND exists
                    (SELECT * FROM business
                        WHERE business.id = coupons.business_id
                        AND business.name = :business_name)
        """
        current_coupon = connection.execute(
            text(query),
            {
                "coupon_name": request.coupon_name,
                "business_name": request.business_name,
            },
        ).first()
        if not current_coupon:
            return f"Could not find a coupon from business {request.business_name} for coupon {request.coupon_name}"

        id = current_coupon.id

        # updating the values of the coupon if they were passed in the request
        name = request.new_coupon_name or current_coupon.name
        is_valid = request.is_valid or current_coupon.valid
        price = request.price or current_coupon.price

        query = text(
            "UPDATE coupons SET name = :name, valid = :is_valid, price = :price WHERE id = :id"
        )
        connection.execute(
            query, {"name": name, "is_valid": is_valid, "price": price, "id": id}
        )
        return "OK"


class GetCouponRequest(BaseModel):
    business_name: str
    coupon_name: str


@router.post("/get")
def get_coupon(request: GetCouponRequest):
    with db.engine.begin() as connection:
        # get the current coupon
        query = """
            Select id, name, valid, price from coupons
                WHERE name = :coupon_name
                    AND exists
                    (SELECT * FROM business
                        WHERE business.id = coupons.business_id
                        AND business.name = :business_name)
        """
        coupon = connection.execute(
            text(query),
            {
                "coupon_name": request.coupon_name,
                "business_name": request.business_name,
            },
        ).first()
        if not coupon:
            return f"Could not find a coupon from business {request.business_name} for coupon {request.coupon_name}"
        return coupon


class CouponRequest(BaseModel):
    coupon_id: int
    user_id: int


@router.post("/purchase")
def post_buy_coupon(request: CouponRequest):
    coupon_id = request.coupon_id
    user_id = request.user_id
    with db.read_repeatable_engine.begin() as connection:
        # checking if the coupon is valid
        query = text("SELECT valid FROM coupons WHERE id = :coupon_id")
        is_valid = connection.execute(
            query, {"coupon_id": request.coupon_id}
        ).scalar_one()
        if not is_valid:
            return "coupon not valid"

        # checking if user can affording the transaction
        query = text(
            """
            SELECT (SELECT SUM(change) FROM user_peepcoin_ledger WHERE user_id = :user_id) >= price
                FROM coupons WHERE id = :coupon_id
            """
        )
        can_afford = connection.execute(
            query, {"user_id": user_id, "coupon_id": coupon_id}
        ).scalar_one()
        if not can_afford:
            return "user can't afford coupon"

        # removing peepcoins from their account
        query = text(
            "INSERT INTO user_peepcoin_ledger (user_id, change) VALUES (:user_id, -1 * (SELECT price FROM coupons where id = :coupon_id))"
        )
        connection.execute(query, {"user_id": user_id, "coupon_id": coupon_id})

        # adding coupon to their account
        query = text(
            "INSERT INTO user_coupon_ledger (user_id, coupon_id, change) VALUES (:user_id, :coupon_id, 1)"
        )
        connection.execute(query, {"user_id": user_id, "coupon_id": coupon_id})
        return "OK"
