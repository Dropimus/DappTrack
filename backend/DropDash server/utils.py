import jwt
from typing import Annotated, Union, Dict, Optional
from datetime import datetime, timedelta, timezone
from createDB import get_session
from fastapi import HTTPException, Depends, status
from schemas import TokenData, UserScheme
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from models import User
import asyncio
import re

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str, db):

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first() 
    if user:
        return user
    else:
        return None


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: Dict[str, str], expires_delta: timedelta) -> str:
    """
    Create a JWT refresh token with specified expiration.

    :param data: Dictionary containing the payload for the token.
    :param expires_delta: timedelta object specifying how long the token should be valid.
    :return: A JWT refresh token as a string.
    """
    # Define token expiration time
    expiration = datetime.utcnow() + expires_delta
    
    # Create the token
    encoded_jwt = jwt.encode(
        {"exp": expiration, **data},
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user

async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(get_session)):
    user = await get_user(username, db)
    print(f'THE USERRRRR: {user}')
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],  
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Convert to Pydantic model (UserScheme) and return
    return UserScheme.from_orm(current_user)

def decode_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if 'exp' in payload:
            expiration_time = datetime.utcfromtimestamp(payload['exp'])
            if expiration_time < datetime.utcnow():
                return None  # Token is expired

        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    
    if not re.search(r"[!@#\$%\^&\*\(\)_\+\-=\[\]\{\};':\"\\|,.<>\/?]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")

    return True

