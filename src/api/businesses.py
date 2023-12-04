from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db


router = APIRouter(
    prefix="/business",
    tags=["businesses"],
    dependencies=[Depends(auth.get_api_key)],
)


class Business(BaseModel):
    name: str
    address: str


@db.handle_errors
@router.put("/add")
def add_business(request: Business):
    with db.engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO business (name, address)
                VALUES (:name, :address)
                """
            ),
            {"name": request.name, "address": request.address},
        )
    return "OK"


class ListBusinessesRequest(BaseModel):
    should_have_valid_coupon: bool


@db.handle_errors
@router.get("/list")
def list_businesses(request: ListBusinessesRequest):
    with db.engine.begin() as connection:
        if request.should_have_valid_coupon:
            query = text(
                """
                select DISTINCT id, name, address from business
                WHERE exists
                    (SELECT * FROM coupons
                    WHERE coupons.business_id = business.id
                        AND coupons.valid)
            """
            )
        else:
            query = text("SELECT DISTINCT id, name, address from business")
        result = connection.execute(query).all()
        if not result:
            return f"Failed to look up businesses"

        return [row._asdict() for row in result]
