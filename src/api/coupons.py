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


@router.post("/business/{business_id}")
def get_valid_coupons_from_business(business_id: int):
    with db.engine.begin() as connection:
        query = text(
            "SELECT name, price from coupons WHERE business_id = :id AND valid"
        )
        result = connection.execute(query, {"id": business_id}).all()
        if not result:
            return f"failed to look up coupons for business_id: {business_id}"

        return [row._asdict() for row in result]


class EditCouponRequest(BaseModel):
    business_id: int
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
                    AND id = :id
        """
        current_coupon = connection.execute(
            text(query),
            {
                "coupon_name": request.coupon_name,
                "id": request.business_id,
            },
        ).first()
        if not current_coupon:
            return f"Could not find a coupon from business id {request.business_id} for coupon {request.coupon_name}"

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
    business_id: int
    coupon_name: str


@router.post("/get")
def get_coupon(request: GetCouponRequest):
    with db.engine.begin() as connection:
        # get the current coupon
        query = """
            Select id, name, valid, price from coupons
                WHERE name = :coupon_name
                    AND id = :id
        """
        coupon = connection.execute(
            text(query),
            {
                "coupon_name": request.coupon_name,
                "id": request.business_id,
            },
        ).first()
        if not coupon:
            return f"Could not find a coupon from business_id {request.business_id} for coupon {request.coupon_name}"
        return coupon


class CouponRequest(BaseModel):
    coupon_id: int
    user_id: int


@router.post("/purchase")
def post_buy_coupon(request: CouponRequest):
    # wrapping function like this so we can test the body of it seperately
    coupon_id = request.coupon_id
    user_id = request.user_id
    with db.read_repeatable_engine.begin() as connection:
        return buy_coupon(coupon_id, user_id, connection)


def buy_coupon(coupon_id: int, user_id: int, connection):
    # checking if the coupon is valid
    query = text("SELECT valid FROM coupons WHERE id = :coupon_id")
    is_valid = connection.execute(query, {"coupon_id": coupon_id}).scalar_one()
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
