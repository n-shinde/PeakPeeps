import sqlalchemy
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


@router.put("/add")
def add_business(request: Business):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO business (name, address)
                VALUES (:name, :address)
                """
            ),
            [{"name": request.name, "address": request.address}],
        )
    return "OK"
