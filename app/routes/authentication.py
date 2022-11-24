from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, security
from app.database import get_database
from app.security import pwd_context

auth_router = APIRouter()


def create_access_token(user: models.User) -> str:
    return security.create_access_token(data={
        "id": user.id,
        "stripe_id": user.stripe_id,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "is_superuser": user.is_superuser,
        "is_employee": user.is_employee
    })

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

    access_token = create_access_token(user)

    response.set_cookie(key="session", value=access_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

   
@auth_router.post("/register", response_model=schemas.authentication.Token)
async def register_new_user(
    response: Response,
    new_user_details: schemas.user.NewUserIn,
    db: AsyncSession = Depends(get_database)
):
    new_user = models.User( 
        email=new_user_details.username,
        firstname=new_user_details.firstname,
        lastname=new_user_details.lastname,
        password=pwd_context.hash(new_user_details.password)
    )

    db.add(new_user)
    await db.commit()
    db.refresh(new_user)

    access_token = create_access_token(new_user)

    response.set_cookie(key="session", value=access_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
