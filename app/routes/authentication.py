from app import schemas, security
from app.database import get_database
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter()


@auth_router.post("/token/", response_model=schemas.authentication.Token)
async def get_access_token(
    response: Response,
    data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_database)
):

    user = await security.get_user_by_email(db, email=data.username)

    if not security.authenticate_user(user, data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = security.create_access_token(data={
        "id": user.id,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "is_superuser": user.is_superuser,
        "is_employee": user.is_employee
    })

    response.set_cookie(key="session", value=access_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
