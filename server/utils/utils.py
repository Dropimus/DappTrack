import jwt
from typing import Annotated, Union, Dict, Optional
from datetime import datetime, timedelta, timezone
from createDB import get_session
from fastapi import HTTPException, Depends, status, WebSocket
from fastapi.responses import JSONResponse
from models.schemas import TokenData, UserScheme
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from utils.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from models.models import User, PointsTransaction
from websocket_manager import manager
import asyncio
import re
import json
import math
import secrets
from services.title_management import update_user_title

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

LEVEL_THRESHOLDS = [0, 50, 150, 300, 500, 800, 1200, 1800, 2500, 3500]

# Utility function for consistent responses
def api_response(success: bool, message: str, data=None, status_code: int = 200):
    # If data is a Pydantic model, convert to dict
    if hasattr(data, "model_dump"):  # Pydantic v2
        data = data.model_dump()
    elif hasattr(data, "dict"):  # Pydantic v1 fallback
        data = data.dict()
    
    return JSONResponse(
        content={
            "success": success,
            "message": message,
            "data": data
        },
        status_code=status_code
    )


def generate_referral_code():
    return secrets.token_hex(4) 

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

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: Dict[str, str], expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)



async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: AsyncSession = Depends(get_session)
):
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
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_session)
):
    # 1) Accept the WS connection so we can read headers
    await websocket.accept()                              # :contentReference[oaicite:0]{index=0}

    # 2) Pull token from header or query‑param
    auth: str = websocket.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
    else:
        token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Missing auth token")

    # 3) Delegate to your existing HTTP get_current_user
    try:
        user = await get_current_user(token, db)          # :contentReference[oaicite:1]{index=1}
    except HTTPException as e:
        # close the socket with policy violation if auth fails
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise e

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


async def calculate_level(points: float) -> int:
    level = 1
    for idx, threshold in enumerate(LEVEL_THRESHOLDS, start=1):
        if points >= threshold:
            level = idx
        else:
            break
    return level

async def update_user_level(db: AsyncSession, user: User) -> None:
    new_level = await calculate_level(user.dapp_points)
    if new_level != user.level:
        user.level = new_level
        await db.commit()


async def record_points_transaction(
    user_id: int,
    txn_type: str,
    amount: float,
    description: str | None,
    reference_id: str,
    db: AsyncSession
) -> float:
    # Check if transaction already exists
    existing = await db.execute(
        select(PointsTransaction).where(
            PointsTransaction.reference_id == reference_id
        )
    )
    if existing.scalars().first():
        print(f"[SKIP] Transaction already exists for reference_id: {reference_id}")
        return 0.0

    # Lock user row to prevent race conditions
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .with_for_update()
    )
    user = result.scalars().first()
    if not user:
        raise ValueError("User not found")

    txn = PointsTransaction(
        user_id=user_id,
        type=txn_type,
        amount=amount,
        description=description,
        reference_id=reference_id,
    )
    db.add(txn)

    user.honor_points += amount
    txn_data = {
        "type": "balance_update",
        "new_balance": user.honor_points,
        "amount": amount,
        "txn_type": txn_type,
        "description": description,
        "message": f"You earned {amount} HONOR" if amount > 0 else f"You lost {-amount} HONOR."
    }

    print(f"TXN: {txn_data}")
    await update_user_title(db, user)
    await manager.send_personal_message(json.dumps(txn_data), user_id)

    await db.commit()
    await db.refresh(user)

    return user.honor_points





