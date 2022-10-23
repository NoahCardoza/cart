import json
import random

from fastapi import FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from app import environ
from app.exceptions import JSONException
from app.routes.search import search_router

app = FastAPI()
app.include_router(search_router, prefix="/search", tags=["search"])

allow_origins = []
allow_origin_regex = None

if environ.DEVELOPMENT:
    # allow all origins in development
    allow_origins = ["*"]

if environ.STAGING:
    # allow local frontend development to access staging backend
    allow_origins.append("http://localhost:3000")
    allow_origins.append("http://127.0.0.1:3000")

    # allow the staging frontend to access staging backend
    allow_origins.append("https://produce-goose-frontend-stg.herokuapp.com")

    # allow review apps to access staging backend
    allow_origin_regex = r"https:\/\/produce-goos-.+\.herokuapp\.com"


app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(json.loads(exc.json()), status_code=422)


@app.exception_handler(JSONException)
async def validation_exception_handler(request, exc):
    return JSONResponse(exc.body, status_code=exc.code)


@app.get("/")
def get_root():
    """And example showing how FastAPI converts python dicts to JSON"""
    return {"message": "Hello World"}


@app.get("/example")
def get_with_query(arg: str = Query(default=None)):
    """An example showing how to use query parameters"""
    return {"arg": arg}


class UserIn(BaseModel):
    """A pydantic model for the information expected from the ui"""
    name: str
    age: int


class UserOut(UserIn):
    """A pydantic model for the information returned to the ui"""
    id: int


@app.post("/validate", response_model=UserOut)
def validate_data(user: UserIn):
    """An example showing how to validate data from the ui and return a response"""
    return {
        "id": random.randint(100, 1000),
        **user.dict(),
    }
