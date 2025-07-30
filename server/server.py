import logging
from fastapi import (
    FastAPI, Depends, HTTPException, Query, status, UploadFile, File, Request, Response, Cookie
)
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import asc, desc, func, exists
from typing import Annotated, Optional, List
from datetime import timedelta, datetime
from cryptography.fernet import Fernet
import os, shutil, json, secrets

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from utils.config import get_settings
from utils.utils import (
    api_response,
    create_access_token,
    create_refresh_token,
    generate_referral_code,
    authenticate_user,
    pwd_context,
    get_current_active_user,
    decode_token,
    verify_password,
    get_password_hash,
    validate_password,
    record_points_transaction
)
from utils.redis import (
    set_cache, get_cache, delete_cache, invalidate_tracked_airdrops_cache,
    set_blacklisted_token, is_token_blacklisted, blacklist_all_user_tokens
)
from routers import submissions
from models.schemas import (
    SignupRequest, LoginRequest, NotificationRequest, FirebaseTokenRequest,
    UpdatePasswordSchema, UserUpdateSchema, AirdropCreateSchema, AirdropTrackRequest,
    TrackedAirdropsResponse,
    TimerRequest, SettingsUpdate, EncryptTokenData, RatingRequestSchema,
    UserScheme, ReferredUser, TrackedAirdropSchema, SettingsSchema,
    UserResponse, UsersListResponse, SettingsResponse, GenericResponse
)
from models.models import User, Submission, AirdropTracking, Timer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECURE = False  # Set to True for production
IS_PRODUCTION = False  # Set to True for production

limiter = Limiter(key_func=get_remote_address)
settings = get_settings()

app = FastAPI(
    title='Dropimus API',
    description="api docs",
    version="1.0.0",
    root_path="/api"
)

app.include_router(submissions.router, prefix="/submissions", tags=["Airdrop Submissions"])
app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

UPLOAD_DIR = "static/airdrop_image"
os.makedirs(UPLOAD_DIR, exist_ok=True)
key = settings.fernet_key
cipher = Fernet(key)

SIGNUP_BONUS_POINTS = 0
AIRDROP_TRACKING_POINTS = 0.0001
REFERRAL_BONUS_POINTS = 0.05

DEFAULT_USER_SETTINGS = {
    "theme": "light",
    "notifications": True,
    "language": "en",
}

# --- CSRF Protection ---
def generate_csrf_token():
    return secrets.token_urlsafe(32)

def verify_csrf(csrf_cookie: Optional[str] = Cookie(None), csrf_header: Optional[str] = None):
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise HTTPException(status_code=403, detail="CSRF token missing or invalid")

@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    # Only check CSRF for state-changing methods
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("x-csrf-token")
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return JSONResponse(status_code=403, content={"success": False, "message": "CSRF token missing or invalid", "data": None})
    response = await call_next(request)
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    msg = "Internal server error" if IS_PRODUCTION else str(exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": msg,
            "data": None
        }
    )

@app.post('/', response_model=GenericResponse)
async def home(response: Response):
    # Set CSRF token cookie for browser clients
    csrf_token = generate_csrf_token()
    response.set_cookie("csrf_token", csrf_token, secure=SECURE, httponly=False, samesite="Lax")
    return api_response(True, "API root", None)

@app.get("/health", response_model=GenericResponse)
async def health():
    return api_response(True, "ok", {"status": "ok"})

@app.post("/verify-token/", response_model=GenericResponse)
async def verify_token(payload: FirebaseTokenRequest):
    try:
        user_data = verify_firebase_token(payload.id_token)
        return api_response(True, "Token verified", {"uid": user_data["uid"], "email": user_data.get("email")})
    except ValueError as e:
        logger.exception("Token verification error")
        msg = "Invalid token" if IS_PRODUCTION else str(e)
        raise HTTPException(status_code=400, detail=msg)

@app.post("/send-notification/", response_model=GenericResponse)
async def send_notification(payload: NotificationRequest):
    try:
        message_id = send_push_notification(payload.token, payload.title, payload.body)
        return api_response(True, "Notification sent", {"message_id": message_id})
    except ValueError as e:
        logger.exception("Notification error")
        msg = "Notification error" if IS_PRODUCTION else str(e)
        raise HTTPException(status_code=400, detail=msg)

@app.post("/signup", response_model=UserResponse)
@limiter.limit("5/minute")
async def create_user(
    payload: SignupRequest,
    db: AsyncSession = Depends(get_session)
):
    validate_password(payload.password)
    stmt = select(User).where(User.email == payload.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        # User enumeration protection
        raise HTTPException(status_code=400, detail="Signup failed. Please try again.")
    stmt = select(User).where(User.username == payload.username)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Signup failed. Please try again.")
    referred_by = None
    referrer = None
    if payload.referral_code:
        result = await db.execute(select(User).where(User.referral_code == payload.referral_code))
        referrer = result.scalars().first()
        if not referrer:
            raise HTTPException(status_code=400, detail="Signup failed. Please try again.")
        await record_points_transaction(
            user_id=referrer.id,
            txn_type="referral_bonus",
            amount=REFERRAL_BONUS_POINTS,
            description=f"Referral Bonus for referring {payload.username}",
            db=db
        )
        referred_by = referrer.id
    hashed_password = pwd_context.hash(payload.password)
    admin_exists = await db.execute(select(exists().where(User.is_admin == True)))
    is_admin = not admin_exists.scalar()
    new_user = User(
        username=payload.username.lower(),
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hashed_password,
        referral_code=generate_referral_code(),
        referred_by=referred_by,
        is_admin=is_admin,
        settings=DEFAULT_USER_SETTINGS.copy()
    )
    db.add(new_user)
    await db.flush()
    try:
        await db.commit()
        await db.refresh(new_user)
        return api_response(
            True,
            "User created successfully",
            {
                "user": UserScheme.from_orm(new_user),
                "honor_points": new_user.honor_points,
                "referral_code": new_user.referral_code,
                "referred_by": new_user.referred_by,
                "is_admin": new_user.is_admin,
                "title": getattr(new_user, "title", None)
            }
        )
    except IntegrityError:
        await db.rollback()
        logger.exception("Integrity error during signup")
        raise HTTPException(status_code=400, detail="Signup failed. Please try again.")
    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error during signup")
        msg = "Signup failed. Please try again." if IS_PRODUCTION else str(e)
        raise HTTPException(status_code=500, detail=msg)

@app.post("/login", response_model=GenericResponse)
@limiter.limit("10/minute")
async def login_for_access_token(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_session),
    response: Response = None
):
    user = await authenticate_user(payload.username, payload.password, db)
    if not user:
        # User enumeration protection
        raise HTTPException(status_code=401, detail="Login failed. Please check your credentials.")
    access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
    refresh_token_expires = timedelta(days=settings.access_token_expires_days if not payload.remember_me else settings.remember_me_refresh_token_expires_days)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
    if payload.remember_me and response:
        response.set_cookie(key='refresh_token', value=refresh_token, secure=SECURE, httponly=True, max_age=int(refresh_token_expires.total_seconds()))
    # Set CSRF token cookie
    csrf_token = generate_csrf_token()
    if response:
        response.set_cookie("csrf_token", csrf_token, secure=SECURE, httponly=False, samesite="Lax")
    return api_response(True, "Login successful", {"access_token": access_token, "token_type": "bearer"})

@app.post("/logout", response_model=GenericResponse)
@limiter.limit("10/minute")
async def logout(
    response: Response,
    request: Request,
    refresh_token: Optional[str] = Cookie(None),
    current_user: Annotated[UserScheme, Depends(get_current_active_user)] = None
):
    try:
        # Blacklist refresh token in Redis
        if refresh_token:
            await set_blacklisted_token(refresh_token)
        response.delete_cookie(key='refresh_token', secure=SECURE)
        response.delete_cookie(key='access_token', secure=SECURE)
        response.delete_cookie(key='csrf_token', secure=SECURE)
        return api_response(True, "Successfully Logged Out", None)
    except Exception as e:
        logger.exception("Logout error")
        msg = "Logout failed." if IS_PRODUCTION else str(e)
        raise HTTPException(status_code=500, detail=msg)

@app.get("/user", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
):
    return api_response(True, "User fetched", UserScheme.from_orm(current_user))

@app.get("/user/{username}", response_model=UserResponse)
async def read_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_session)
):
    user = await db.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return api_response(True, "User fetched", UserScheme.from_orm(user))

@app.get("/user/referrals", response_model=UsersListResponse)
async def get_my_referrals(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    user_id = current_user.id
    stmt = select(User).where(User.referred_by == user_id)
    result = await db.execute(stmt)
    referred_users = result.scalars().all()
    return api_response(True, "Referrals fetched", [ReferredUser.from_orm(u) for u in referred_users])

@app.put("/user/edit", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_user_info(
    payload: UserUpdateSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    csrf_token: Optional[str] = Cookie(None),
    x_csrf_token: Optional[str] = None
):
    verify_csrf(csrf_token, x_csrf_token)
    user = await db.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return api_response(True, "User updated", UserScheme.from_orm(user))

@app.put("/user/password", response_model=GenericResponse)
@limiter.limit("10/minute")
async def update_user_password(
    payload: UpdatePasswordSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    csrf_token: Optional[str] = Cookie(None),
    x_csrf_token: Optional[str] = None
):
    verify_csrf(csrf_token, x_csrf_token)
    user = await db.get(User, current_user.id)
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Password update failed.")
    if payload.new_password != payload.confirm_new_password:
        raise HTTPException(status_code=400, detail="Password update failed.")
    user.password_hash = get_password_hash(payload.new_password)
    await db.commit()
    await db.refresh(user)
    # Blacklist all refresh tokens for this user (by user ID)
    await blacklist_all_user_tokens(user.id)
    return api_response(True, "Password updated successfully", None)

@app.post("/token/refresh", response_model=GenericResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    refresh_token: Optional[str] = Cookie(None)
):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token not provided")
    if await is_token_blacklisted(refresh_token):
        raise HTTPException(status_code=401, detail="Token revoked. Please login again.")
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
    new_access_token = create_access_token(data={"sub": payload["sub"]}, expires_delta=access_token_expires)
    return api_response(True, "Token refreshed", {"access_token": new_access_token, "token_type": "bearer"})

@app.post("/encrypt", response_model=GenericResponse)
async def encrypt(tokens: EncryptTokenData):
    try:
        if tokens.access_token:
            encrypted_access_token = cipher.encrypt(tokens.access_token.encode()).decode()
        else:
            raise HTTPException(status_code=400, detail="Access token is required")
        encrypted_refresh_token = None
        if tokens.refresh_token:
            encrypted_refresh_token = cipher.encrypt(tokens.refresh_token.encode()).decode()
        return api_response(
            True,
            "Tokens encrypted",
            {
                "access_token": encrypted_access_token,
                "refresh_token": encrypted_refresh_token
            }
        )
    except Exception as e:
        logger.exception("Encryption error")
        msg = "Encryption failed." if IS_PRODUCTION else f"Encryption error: {str(e)}"
        raise HTTPException(status_code=500, detail=msg)

@app.post("/decrypt", response_model=GenericResponse)
async def decrypt_data(tokens: EncryptTokenData):
    try:
        if tokens.access_token:
            decrypted_access_token = cipher.decrypt(tokens.access_token.encode()).decode()
            decrypted_refresh_token = None
            if tokens.refresh_token:
                decrypted_refresh_token = cipher.decrypt(tokens.refresh_token.encode()).decode()
            response = {
                "access_token": decrypted_access_token
            }
            if decrypted_refresh_token:
                response["refresh_token"] = decrypted_refresh_token
            return api_response(True, "Tokens decrypted", response)
        else:
            raise HTTPException(status_code=400, detail="Access token is required")
    except Exception as e:
        logger.exception("Decryption error")
        msg = "Decryption failed." if IS_PRODUCTION else "Decryption failed"
        raise HTTPException(status_code=500, detail=msg)

@app.post("/user/tracked/add", response_model=GenericResponse)
@limiter.limit("10/minute")
async def track_airdrop(
    payload: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    csrf_token: Optional[str] = Cookie(None),
    x_csrf_token: Optional[str] = None
):
    verify_csrf(csrf_token, x_csrf_token)
    try:
        existing = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, submission_id=payload.submission_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Already tracking this airdrop")
        airdrop = await db.execute(select(Submission).filter_by(id=payload.submission_id))
        airdrop = airdrop.scalar_one_or_none()
        if not airdrop:
            raise HTTPException(status_code=404, detail="Airdrop not found")
        tracking = AirdropTracking(user_id=current_user.id, submission_id=payload.submission_id)
        db.add(tracking)
        await db.commit()
        await invalidate_tracked_airdrops_cache(current_user.id)
        return api_response(True, "Airdrop successfully added to tracking", None)
    except IntegrityError:
        await db.rollback()
        logger.exception("Integrity error during tracking")
        raise HTTPException(status_code=400, detail="Already tracking this airdrop")
    except Exception as e:
        await db.rollback()
        logger.exception("Error tracking airdrop")
        msg = "Tracking failed." if IS_PRODUCTION else f"Error tracking airdrop: {str(e)}"
        raise HTTPException(status_code=500, detail=msg)

@app.post("/user/tracked/remove", response_model=GenericResponse)
@limiter.limit("10/minute")
async def untrack_airdrop(
    payload: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    csrf_token: Optional[str] = Cookie(None),
    x_csrf_token: Optional[str] = None
):
    verify_csrf(csrf_token, x_csrf_token)
    try:
        existing = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, submission_id=payload.submission_id)
        )
        tracking = existing.scalar_one_or_none()
        if not tracking:
            raise HTTPException(status_code=400, detail="Airdrop is not being tracked")
        await db.delete(tracking)
        others = await db.execute(
            select(AirdropTracking).filter_by(submission_id=payload.submission_id)
        )
        others = others.scalars().all()
        if not others:
            airdrop_result = await db.execute(
                select(Submission).filter_by(id=payload.submission_id)
            )
            airdrop = airdrop_result.scalar_one_or_none()
            if airdrop:
                airdrop.is_tracked = False
                db.add(airdrop)
        await db.commit()
        await invalidate_tracked_airdrops_cache(current_user.id)
        return api_response(True, "Airdrop successfully removed from tracking", None)
    except Exception as e:
        await db.rollback()
        logger.exception("Error untracking airdrop")
        msg = "Untracking failed." if IS_PRODUCTION else f"Error untracking airdrop: {str(e)}"
        raise HTTPException(status_code=500, detail=msg)

@app.get("/user/tracked", response_model=TrackedAirdropsResponse)
async def get_tracked_airdrops(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    cache_key = f"user:{current_user.id}:tracked_airdrops:{limit}:{offset}"
    cached_data = await get_cache(cache_key)
    if cached_data:
        cached_list = [TrackedAirdropSchema(**item) for item in json.loads(cached_data)]
        return api_response(True, "Tracked airdrops fetched (cache)", cached_list)
    tracked_airdrops = await db.execute(
        select(Submission)
        .join(AirdropTracking)
        .filter(AirdropTracking.user_id == current_user.id)
        .offset(offset)
        .limit(limit)
    )
    tracked_airdrops = tracked_airdrops.scalars().all()
    response_data = []
    for airdrop in tracked_airdrops:
        task_progress = 0.0  # placeholder
        schema = TrackedAirdropSchema.from_orm_with_duration(airdrop, task_progress)
        schema.id = airdrop.id
        response_data.append(schema)
    await set_cache(cache_key, json.dumps([d.dict() for d in response_data]), expire=3600)
    return api_response(True, "Tracked airdrops fetched", response_data)

@app.get("/user/tracked/count", response_model=GenericResponse)
async def get_tracked_airdrops_count(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    try:
        count_result = await db.execute(
            select(func.count()).select_from(AirdropTracking).filter(
                AirdropTracking.user_id == current_user.id
            )
        )
        count = count_result.scalar()
        return api_response(True, "Tracked airdrop count fetched", {"total_tracked": count})
    except Exception as e:
        logger.exception("Error fetching tracked airdrop count")
        msg = "Fetch failed." if IS_PRODUCTION else f"Error fetching tracked airdrop count: {str(e)}"
        raise HTTPException(status_code=500, detail=msg)

@app.post("/user/set_timer", response_model=GenericResponse)
@limiter.limit("10/minute")
async def set_timer(
    payload: TimerRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    csrf_token: Optional[str] = Cookie(None),
    x_csrf_token: Optional[str] = None
):
    verify_csrf(csrf_token, x_csrf_token)
    try:
        airdrop_query = await db.execute(select(Submission).where(Submission.id == payload.submission_id))
        airdrop = airdrop_query.scalars().first()
        if not airdrop:
            raise HTTPException(status_code=404, detail="Airdrop not found")
        next_reminder_time = datetime.utcnow() + timedelta(seconds=payload.total_seconds)
        new_timer = Timer(
            user_id=current_user.id,
            submission_id=payload.submission_id,
            reminder_interval=payload.total_seconds,
            next_reminder_time=next_reminder_time,
            is_active=True
        )
        db.add(new_timer)
        await db.commit()
        await db.refresh(new_timer)
        return api_response(
            True,
            "Timer set successfully",
            {
                "timer_id": new_timer.id,
                "next_reminder_time": next_reminder_time
            }
        )
    except Exception as e:
        await db.rollback()
        logger.exception("Error setting timer")
        msg = "Set timer failed." if IS_PRODUCTION else f"Error setting timer: {str(e)}"
        raise HTTPException(status_code=500, detail=msg)

@app.patch("/user/settings", response_model=SettingsResponse)
@limiter.limit("10/minute")
async def update_settings(
    payload: SettingsUpdate,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    csrf_token: Optional[str] = Cookie(None),
    x_csrf_token: Optional[str] = None
):
    verify_csrf(csrf_token, x_csrf_token)
    merged = {**DEFAULT_USER_SETTINGS, **(current_user.settings or {}), **payload.settings}
    current_user.settings = merged
    await db.commit()
    await db.refresh(current_user)
    return api_response(True, "Settings updated", {"user_id": current_user.id, "settings": merged})

@app.post("/airdrop/rate", response_model=GenericResponse)
@limiter.limit("10/minute")
async def rate_airdrop(
    payload: RatingRequestSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    csrf_token: Optional[str] = Cookie(None),
    x_csrf_token: Optional[str] = None
):
    verify_csrf(csrf_token, x_csrf_token)
    airdrop = await db.execute(select(Submission).where(Submission.id == payload.submission_id))
    airdrop = airdrop.scalars().first()
    if not airdrop:
        raise HTTPException(status_code=404, detail="Airdrop not found")
########################
    from models.models import Rating
    existing_rating = await db.execute(
        select(Rating).where(
            Rating.user_id == current_user.id,
            Rating.submission_id == payload.submission_id
        )
    )
    rating_obj = existing_rating.scalars().first()
    if rating_obj:
        rating_obj.rating = payload.rating
        rating_obj.updated_at = datetime.utcnow()
    else:
        rating_obj = Rating(
            user_id=current_user.id,
            submission_id=payload.submission_id,
            rating=payload.rating,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(rating_obj)
    await db.commit()
    return api_response(True, "Airdrop rated", {"submission_id": payload.submission_id, "rating": payload.rating})

@app.get("/users", response_model=UsersListResponse)
@limiter.limit("10/minute")
async def get_all_users(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    stmt = select(User).offset(offset).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    if not users:
        return api_response(False, "No users found", [])
    return api_response(True, "Users fetched", [UserScheme.from_orm(u) for u in users])