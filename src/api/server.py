from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import routes
from src.api import reviews
from src.api import peepcoins
from src.api import businesses
from src.api import coupons
from src.api import users
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware


description = """
Find the best routes your friends love on PeakPeeps!
"""

app = FastAPI(
    title="PeakPeeps",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Robin Tun",
        "email": "rotun@calpoly.edu",
    },
)

# origins = ["https://potion-exchange.vercel.app"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "OPTIONS"],
#     allow_headers=["*"],
# )


app.include_router(routes.router)
app.include_router(reviews.router)
app.include_router(peepcoins.router)
app.include_router(businesses.router)
app.include_router(coupons.router)
app.include_router(users.router)


@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response["message"].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)


@app.get("/")
async def root():
    return {"message": "Welcome to PeakPeeps"}
