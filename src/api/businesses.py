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

        business = connection.execute(
            text(
                """
                SELECT id
                FROM business
                WHERE name = :name
                """
            ),
            {"name": request.name}
        ).scalars()

        if business:
            raise HTTPException(status_code=404, detail="Business already exists")
        
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


@db.handle_errors
@router.get("/list")
def list_businesses():
    with db.engine.begin() as connection:

        result = connection.execute(
            text(
            """
            SELECT DISTINCT id, name, address
            FROM business
            JOIN coupons ON business.id = coupons.business_id
            WHERE coupons.valid 
            """
            )
        ).fetchall()

    return [{"id": row[0], "name": row[1], "address": row[2]} for row in result]