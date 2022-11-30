from datetime import datetime, timedelta
from traceback import print_exc

from app import environ, models, schemas
from app.environ import COOKIE_DOMAIN, PRODUCTION
from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

JWT_ALGORITHM = "HS256"
COOKIE_EXPIRE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=environ.JWT_EXPIRE_TIMEOUT_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, environ.JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def set_access_token_cookie(response: Response, access_token: str):
    expires = datetime.utcnow() + timedelta(minutes=environ.JWT_EXPIRE_TIMEOUT_MINUTES)
    
    cookie = {
        'key': 'session',
        'value': access_token,
        'expires': expires.strftime(COOKIE_EXPIRE_FORMAT),
        'httponly': True
    }

    if PRODUCTION:
        cookie['domain'] = COOKIE_DOMAIN
        cookie['secure'] = True
        cookie['samesite'] = 'none'

    response.set_cookie(**cookie)


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
