from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy import 
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, security
from app.database import get_database

from app.security import pwd_context

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

   
@auth_router.post("/register", response_model=schemas.authentication.Token)
async def register_new_user(
    response: Response,
    newUserDetails: schemas.user.NewUserIn,
    db: AsyncSession = Depends(get_database)
):
    newUser = models.User( 
        email=newUserDetails.username,
        firstname=newUserDetails.firstname,
        lastname=newUserDetails.lastname,
        password=pwd_context.hash(newUserDetails.password)
    )
    db.add(newUser)
    await db.commit()
    db.refresh(newUser)

    access_token = security.create_access_token(data={
        "id": newUser.id,
        "email": newUser.email,
        "firstname": newUser.firstname,
        "lastname": newUser.lastname,
        "is_superuser": newUser.is_superuser,
        "is_employee": newUser.is_employee
    })

    response.set_cookie(key="session", value=access_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
