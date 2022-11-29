from datetime import datetime, timedelta
from traceback import print_exc
from typing import Union

from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import environ, models, schemas

JWT_ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=environ.JWT_EXPIRE_TIMEPUT_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, environ.JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_user_by_email(db: AsyncSession, email: str) -> models.User:
    stmt = select(models.User).where(models.User.email == email)
    res = await db.execute(stmt)
    return res.scalars().first()


async def get_current_user(response: Response, session: str = Cookie(...)) -> schemas.user.UserContext:
    try:
        payload = jwt.decode(session, environ.JWT_SECRET,
                             algorithms=[JWT_ALGORITHM])
        return schemas.user.UserContext(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except ValidationError as e:
        print_exc(e)
        response.delete_cookie("session")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credentials invalid",
            headers={"set-cookie": response.headers['set-cookie']}
        )
    except Exception as e:
        print_exc(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fatal error while validating credentials",
        )


async def get_current_superuser(user: schemas.user.UserContext = Depends(get_current_user)) -> schemas.user.UserContext:
    """Checks if the user is a superuser.

    Args:
        user (schemas.user.UserContext): Depends(get_current_user).

    Raises:
        HTTPException: If the user is not a superuser.

    Returns:
        schemas.user.UserContext: The user object.
    """
    if user.is_superuser:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="This route if for superusers only",
    )
    

async def get_current_employee(user: schemas.user.UserContext = Depends(get_current_user)) -> schemas.user.UserContext:
    """Checks if the user is an employee or a superuser.

    Args:
        user (schemas.user.UserContext): Depends(get_current_user).

    Raises:
        HTTPException: If the user is not an employee or superuser.

    Returns:
        schemas.user.UserContext: The user object.
    """
    if user.is_employee or user.is_superuser:
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="This route is for employees only",
    )

def authenticate_user(user: models.User, password: str):
    if user is None:
        return False
    return verify_password(password, user.password)
