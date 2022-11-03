from fastapi import FastAPI
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel

EndPoint = FastAPI()

@EndPoint.get("/")
async def root():
    await Vegetables()
    await Fruits()
    await Meats()

class User(BaseModel):
    id: Optional[UUID] = uuid4
    First_Name: str
    Last_Name: str

EndPoint.post("/api/v1/users")
async def register_user(user:User):
    db.append(user)
    return {"id": user.id}
    

Vegetables()
{
    "id": 1,
    "name": "Vegetables",
    "description": "Spinach", "Carrots", "Green Cabbage", "Purple Cabbage";
}

Fruits()
{
    "id": 1,
    "name": "Fruits",
    "description": "Apple", "Orange", "Strawberry", "Banana";
}

Meats()
{
    "id": 1,
    "name": "Meats",
    "description": "Beef", "Chicken", "Turkey",;
}