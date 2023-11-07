import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
from src import database as db


router = APIRouter(
    prefix="/coupons",
    tags=["coupons"],
    dependencies=[Depends(auth.get_api_key)],
)