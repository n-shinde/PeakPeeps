from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from src.api import auth
from src import database as db
from src.database import get_id_from_business
from src.database import get_id_from_username
from src.database import get_id_from_coupons

router = APIRouter(
    prefix="/coupons",
    tags=["coupons"],
    dependencies=[Depends(auth.get_api_key)],
)


class Coupons(BaseModel):
    business_name: str
    name: str
    price: int


@db.handle_errors
@router.put("/add")
def add_coupon(request: Coupons):
    with db.engine.begin() as connection:

        #valid business check
        business_id = get_id_from_business(request.business_name, connection)

        if business_id is None:
             raise HTTPException(status_code=404, detail="Business does not exist")

        # unique coupon check 
        coupon_id = get_id_from_coupons(request.name, connection)

        if coupon_id:
            raise HTTPException(status_code=404, detail="Coupon with the same name already exists")

        connection.execute(
            text(
                """
                INSERT INTO coupons (business_id, name, price, valid)
                VALUES (:bus_id, :name, :price, True)
                """
            ),
                {
                    "bus_id": business_id,
                    "name": request.name,
                    "price": request.price,
                }
        )
    return "OK"


@db.handle_errors
@router.post("/business/{business_name}")
def get_valid_coupons_from_business(business_name: str):
    with db.engine.begin() as connection:
        business_id = get_id_from_business(business_name, connection)

        if business_id is None:
             raise HTTPException(status_code=404, detail="Business does not exist")
        
        query = text(
            "SELECT name, price from coupons WHERE business_id = :id AND valid"
        )
        result = connection.execute(query, {"id": business_id}).all()

        if not result:
            return f"failed to look up coupons for business: {business_name}"

        return [row._asdict() for row in result]


class EditCouponRequest(BaseModel):
    business_name: str
    coupon_name: str
    new_coupon_name: Optional[str]
    is_valid: bool
    price: Optional[int]


@db.handle_errors
@router.post("/edit")
def edit_coupon(request: EditCouponRequest):
    with db.engine.begin() as connection:

        # valid business check
        business_id = get_id_from_business(request.business_name, connection)

        if business_id is None:
             raise HTTPException(status_code=404, detail="Business does not exist")
        
        #valid coupon check
        coupon_id = get_id_from_coupons(request.coupon_name, connection)

        if coupon_id is None:
             raise HTTPException(status_code=404, detail="Coupon does not exist")
        
        # get the current coupon
        query = """
            SELECT id, name, valid, price
            FROM coupons
            WHERE name = :coupon_name AND business_id = :business_id
        """
        current_coupon = connection.execute(
            text(query),
            {
                "coupon_name": request.coupon_name,
                "business_id": business_id,
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


# @db.handle_errors
# @router.post("/get")
# def get_coupon(request: GetCouponRequest):
#     with db.engine.begin() as connection:
#         business_id = get_id_from_business(request.business_name, connection)

#         if business_id is None:
#              raise HTTPException(status_code=404, detail="Business does not exist")
        
#         #valid coupon check
#         coupon_id = get_id_from_business(request.coupon_name, connection)

#         if coupon_id is None:
#              raise HTTPException(status_code=404, detail="Coupon does not exist")
        
#         # get the current coupon
#         query = """
#             SELECT id, name, valid, price 
#             FROM coupons
#             WHERE name = :coupon_name AND id = :id
#         """
#         coupon = connection.execute(
#             text(query),
#             {
#                 "coupon_name": request.coupon_name,
#                 "id": business_id,
#             },
#         ).first()

#         if not coupon:
#             return f"Could not find a coupon from business {request.business_name} for coupon {request.coupon_name}"
        
#         return coupon


class CouponRequest(BaseModel):
    coupon_name: str
    username: str



@db.handle_errors
@router.post("/purchase")
def post_buy_coupon(coupon_name: str, username: str):

    with db.engine.begin() as connection:
        user_id = get_id_from_username(username, connection)

        if user_id is None:
            raise HTTPException(status_code=404, detail="User does not exist")
    
        # checking if the coupon is valid
        coupon_id = get_id_from_coupons(coupon_name, connection)

        if coupon_id is None:
            raise HTTPException(status_code=404, detail="Coupon does not exist")
    
        query = text("SELECT valid FROM coupons WHERE name = :coupon_name")
        is_valid = connection.execute(query, {"coupon_name": coupon_name}).scalar_one()

        if not is_valid:
            return "Coupon not valid. Cannot purchase."
    

        # checking if user can affording the transaction
        query = text(
            """
            SELECT (SELECT SUM(change) FROM user_peepcoin_ledger WHERE user_id = :user_id) >= price
            FROM coupons 
            WHERE name = :coupon_name
            """
        )
        can_afford = connection.execute(
            query, {"user_id": user_id, "coupon_name": coupon_name}
        ).scalar_one()

        if not can_afford:
            return "Not enough PeepCoins to purchase coupon. Please select another coupon to purchase."

        # removing peepcoins from their account
        query = text(
            "INSERT INTO user_peepcoin_ledger (user_id, change) VALUES (:user_id, -1 * (SELECT price FROM coupons where name = :coupon_name))"
        )
        connection.execute(query, {"user_id": user_id, "coupon_name": coupon_name})

        # adding coupon to their account
        query = text(
            "INSERT INTO user_coupon_ledger (user_id, coupon_id, change) VALUES (:user_id, :coupon_id, 1)"
        )
        connection.execute(query, {"user_id": user_id, "coupon_id": coupon_id})

        return "OK"
