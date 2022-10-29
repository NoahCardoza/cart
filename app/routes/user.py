from app import schemas, security
from fastapi import APIRouter, Depends

user_router = APIRouter()


@user_router.get("/me/", response_model=schemas.user.UserContext)
async def get_me(user: schemas.user.UserContext = Depends(security.get_current_user)):
    """Get the current user."""
    return user
