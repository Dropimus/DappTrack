import logging
from fastapi import (
    FastAPI, Depends, HTTPException, Query, status, UploadFile, File, Request, Response, Cookie, Path
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import asc, desc, func, exists
from typing import Annotated, Optional, List
from datetime import timedelta, datetime, timezone
from cryptography.fernet import Fernet
import os, shutil, json, secrets
from createDB import get_session
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
    set_cache, get_cache, add_user_token, invalidate_tracked_airdrops_cache, blacklist_all_user_tokens,
    set_blacklisted_token, is_token_blacklisted
) 
from utils.firebase import (
    verify_firebase_token, send_push_notification, send_bulk_notifications
)
from routers import verification
from models.schemas import (
    SignupRequest, LoginRequest, NotificationRequest, FirebaseTokenRequest,
    UpdatePasswordSchema, UserUpdateSchema, AirdropCreateSchema, AirdropResponse, AirdropTrackRequest,
    TrackedAirdropsResponse, AirdropStepCreate, AirdropStepResponse,
    TimerRequest, UserSettingsResponse, TokenData, RefreshTokenRequest, RatingRequestSchema,
    UserScheme, ReferredUser, TrackedAirdropSchema, SettingsSchema,
    UserResponse, UsersListResponse, SettingsResponse, GenericResponse
)
from models.models import User, Submission, AirdropTracking, Timer, AirdropStep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECURE = False  # Set to True for production
IS_PRODUCTION = False  # Set to True for production
BASE_URL = "http://localhost" # Change to production URL

limiter = Limiter(key_func=get_remote_address)
settings = get_settings()

app = FastAPI(
    title='Dropimus API',
    description="api docs",
    version="1.0.0",
    root_path="/api"
)

app.include_router(verification.router, prefix="/verification", tags=["Airdrop Submissions Verification"])
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




allowed_origins = [
    "https://dropimus.com",
    "http://localhost:3000"  # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




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



@app.get("/health", response_model=GenericResponse)
async def health():
    return api_response(True, "ok", {"status": "ok"})

#  TODO: test after integrations with fronend is complete
@app.post("/verify-token/", response_model=GenericResponse)
async def verify_token(payload: FirebaseTokenRequest):
    try:
        user_data = verify_firebase_token(payload.id_token)
        return api_response(True, "Token verified", {
            "uid": user_data["uid"],
            "email": user_data.get("email")
        })
    except ValueError:
        logger.exception("Token verification error")
        msg = "Invalid token" if IS_PRODUCTION else "Token verification failed"
        return api_response(False, msg, None)
    except Exception:
        logger.exception("Unexpected error during token verification")
        msg = "Verification failed." if IS_PRODUCTION else "Unexpected error during token verification"
        return api_response(False, msg, None)


@app.post("/send-notification/", response_model=GenericResponse)
async def send_notification(payload: NotificationRequest):
    try:
        message_id = send_push_notification(payload.token, payload.title, payload.body)
        return api_response(True, "Notification sent", {"message_id": message_id})
    except ValueError:
        logger.exception("Notification error")
        msg = "Notification error" if IS_PRODUCTION else "Failed to send notification"
        return api_response(False, msg, None)
    except Exception:
        logger.exception("Unexpected error during notification")
        msg = "Notification failed." if IS_PRODUCTION else "Unexpected error during notification"
        return api_response(False, msg, None)
    
@app.post("/send-bulk-notifications/", response_model=GenericResponse)
async def send_bulk_notifications(payload: NotificationRequest):
    try:
        message_ids = send_bulk_notifications(payload.tokens, payload.title, payload.body)
        return api_response(True, "Bulk notifications sent", {"message_ids": message_ids})
    except ValueError:
        logger.exception("Bulk notification error")
        msg = "Bulk notification error" if IS_PRODUCTION else "Failed to send bulk notifications"
        return api_response(False, msg, None)
##########

@app.post("/token/refresh", response_model=GenericResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    payload: RefreshTokenRequest
):
    try:
        refresh_token = payload.refresh_token

        # Check if token is blacklisted
        if await is_token_blacklisted(refresh_token):
            return api_response(False, "Token revoked. Please login again.", None, status_code=401)

        # Decode token and validate type
        token_data = decode_token(refresh_token)
        if not token_data or token_data.get("type") != "refresh":
            return api_response(False, "Invalid refresh token", None, status_code=401)

        # Blacklist old refresh token (rotation)
        await set_blacklisted_token(refresh_token)

        # Generate new tokens
        access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
        refresh_token_expires = timedelta(days=settings.access_token_expires_days)

        new_access_token = create_access_token(
            data={"sub": token_data["sub"]},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": token_data["sub"]},
            expires_delta=refresh_token_expires
        )

        return api_response(True, "Token refreshed successfully", {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        })

    except Exception as e:
        logger.exception("Error refreshing token")
        msg = "Token refresh failed." if IS_PRODUCTION else f"Error: {str(e)}"
        return api_response(False, msg, None, status_code=500)



@app.post("/encrypt", response_model=GenericResponse)
async def encrypt(tokens: TokenData):
    try:
        if tokens.access_token:
            encrypted_access_token = cipher.encrypt(tokens.access_token.encode()).decode()
        else:
            return api_response(False, "Access token is required", None, status_code=400)
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
        return api_response(False, msg, None)
    
@app.post("/decrypt", response_model=GenericResponse)
async def decrypt_data(tokens: TokenData):
    try:
        if not tokens.access_token:
            return api_response(False, "Access token is required", None)

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

    except Exception as e:
        logger.exception("Decryption error")
        msg = "Decryption failed." if IS_PRODUCTION else f"Decryption error: {str(e)}"
        return api_response(False, msg, None)



@app.post("/signup", response_model=GenericResponse)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    payload: SignupRequest,
    db: AsyncSession = Depends(get_session)
):
    try:
        # Validate password
        validate_password(payload.password)

        # Check if email already exists
        email_check = await db.execute(select(User).where(User.email == payload.email))
        if email_check.scalars().first():
            msg = "Email already in use." if not IS_PRODUCTION else "Signup failed. Please try again."
            return api_response(False, msg)

        # Check if username already exists
        username_check = await db.execute(select(User).where(User.username == payload.username))
        if username_check.scalars().first():
            msg = "Username already taken." if not IS_PRODUCTION else "Signup failed. Please try again."
            return api_response(False, msg)

        # Handle referral code (if provided)
        referred_by = None
        if payload.referral_code:
            referrer_result = await db.execute(select(User).where(User.referral_code == payload.referral_code))
            referrer = referrer_result.scalars().first()
            if not referrer:
                msg = "Invalid referral code." if not IS_PRODUCTION else "Signup failed. Please try again."
                return api_response(False, msg)

            # Add referral bonus for the referrer
            await record_points_transaction(
                user_id=referrer.id,
                txn_type="referral_bonus",
                amount=REFERRAL_BONUS_POINTS,
                description=f"Referral bonus for inviting {payload.username}",
                reference_id=f"user-{referrer.id}",
                db=db
            )
            referred_by = referrer.id

        # Hash password
        hashed_password = pwd_context.hash(payload.password)

        # Determine if this user is the first admin
        admin_exists = await db.execute(select(exists().where(User.is_admin == True)))
        is_admin = not admin_exists.scalar()

        # Create new user instance
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
        await db.commit()
        await db.refresh(new_user)

        # Generate tokens
        access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
        refresh_token_expires = timedelta(days=settings.access_token_expires_days)
        access_token = create_access_token({"sub": new_user.username}, access_token_expires)
        refresh_token = create_refresh_token({"sub": new_user.username}, refresh_token_expires)

        # Store refresh token for global logout
        await add_user_token(str(new_user.id), refresh_token)

        return api_response(True, "User created successfully",)

    except IntegrityError:
        await db.rollback()
        logger.exception("Integrity error during signup")
        return api_response(False, "Signup failed. Please try again.")

    except Exception as e:
        await db.rollback()
        logger.exception("Unexpected error during signup")
        msg = "Signup failed. Please try again." if IS_PRODUCTION else f"Signup failed: {str(e)}"
        return api_response(False, msg)



@app.post("/login", response_model=GenericResponse)
@limiter.limit("10/minute")
async def login_for_access_token(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_session)
):
    try:
        user = await authenticate_user(payload.username, payload.password, db)
        if not user:
            msg = "Login failed. Please check your credentials." if IS_PRODUCTION else "Invalid username or password."
            return api_response(False, msg, None)

        access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
        refresh_token_expires = timedelta(
            days=settings.access_token_expires_days if not payload.remember_me else settings.remember_me_refresh_token_expires_days
        )

        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

        # Store refresh token for global logout
        await add_user_token(str(user.id), refresh_token)

        return api_response(True, "Login successful", {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        })

    except Exception as e:
        logger.exception("Unexpected error during login")
        msg = "Login failed. Please try again." if IS_PRODUCTION else f"Login failed: {str(e)}"
        return api_response(False, msg, None)


@app.post("/logout", response_model=GenericResponse)
@limiter.limit("10/minute")
async def logout(
    request: Request,
    refresh_token: str):
    try:
        await set_blacklisted_token(refresh_token)
        return api_response(True, "Successfully Logged Out", None)
    except Exception as e:
        msg = "Logout failed." if IS_PRODUCTION else f"Logout failed: {str(e)}"
        return api_response(False, msg, None)


@app.get("/user", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
):
    return api_response(True, "User fetched", UserScheme.from_orm(current_user))


@app.get("/user/referrals", response_model=UsersListResponse)
async def get_my_referrals(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    user_id = current_user.id
    stmt = select(User).where(User.referred_by == user_id)
    result = await db.execute(stmt)
    referred_users = result.scalars().all()

    referrals_list = [ReferredUser.from_orm(u).model_dump(mode="json") for u in referred_users]

    return api_response(True, "Referrals fetched", referrals_list)


@app.put("/user/edit", response_model=UserResponse)
@limiter.limit("10/minute")
async def update_user_info(
    request: Request,
    payload: UserUpdateSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),  
): 
    user = await db.get(User, current_user.id)
    if not user:
        return api_response(False, "User not found", None, status_code=404)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return api_response(True, "User updated", UserScheme.from_orm(user))

@app.put("/user/password", response_model=GenericResponse)
@limiter.limit("10/minute")
async def update_user_password(
    request: Request,
    payload: UpdatePasswordSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
):
    try:
        user = await db.get(User, current_user.id)
        if not user:
            return api_response(False, "User not found", None, status_code=404)

        # Validate current password
        if not verify_password(payload.current_password, user.password_hash):
            return api_response(False, "Current password is incorrect", None, status_code=400)

        # Validate new passwords match
        if payload.new_password != payload.confirm_new_password:
            return api_response(False, "New passwords do not match", None, status_code=400)

        # Update password
        user.password_hash = get_password_hash(payload.new_password)
        await db.commit()
        await db.refresh(user)

        # Blacklist all refresh tokens for this user (force re-login)
        await blacklist_all_user_tokens(user.id)

        return api_response(True, "Password updated successfully", None)

    except Exception as e:
        await db.rollback()
        logger.exception("Error updating user password")
        msg = "Password update failed." if IS_PRODUCTION else f"Error: {str(e)}"
        return api_response(False, msg, None, status_code=500)




@app.post("/user/tracked/add", response_model=GenericResponse)
@limiter.limit("10/minute")
async def track_airdrop(
    request: Request,
    payload: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    try:
        # Check if already tracking
        existing = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, submission_id=payload.submission_id)
        )
        if existing.scalar_one_or_none():
            return api_response(False, "Already tracking this airdrop", None)

        # Check if airdrop exists
        airdrop = await db.execute(select(Submission).filter_by(id=payload.submission_id))
        airdrop = airdrop.scalar_one_or_none()
        if not airdrop:
            return api_response(False, "Airdrop not found", None)

        # Add tracking
        tracking = AirdropTracking(user_id=current_user.id, submission_id=payload.submission_id)
        db.add(tracking)
        await db.commit()

        # Invalidate cache for tracked airdrops
        await invalidate_tracked_airdrops_cache(current_user.id)

        return api_response(True, "Airdrop successfully added to tracking", None)

    except IntegrityError:
        await db.rollback()
        logger.exception("Integrity error during tracking")
        return api_response(False, "Already tracking this airdrop", None)

    except Exception:
        await db.rollback()
        logger.exception("Error tracking airdrop")
        msg = "Tracking failed." if IS_PRODUCTION else "Error tracking airdrop"
        return api_response(False, msg, None)
    
@app.post("/user/tracked/remove", response_model=GenericResponse)
@limiter.limit("10/minute")
async def untrack_airdrop(
    request: Request,
    payload: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    try:
        # Check if tracking exists
        existing = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, submission_id=payload.submission_id)
        )
        tracking = existing.scalar_one_or_none()
        if not tracking:
            return api_response(False, "Airdrop is not being tracked", None)

        # Remove tracking
        await db.delete(tracking)

        # Check if others are tracking it; if not, update airdrop status
        others = await db.execute(
            select(AirdropTracking).filter_by(submission_id=payload.submission_id)
        )
        if not others.scalars().first():
            airdrop_result = await db.execute(
                select(Submission).filter_by(id=payload.submission_id)
            )
            airdrop = airdrop_result.scalar_one_or_none()
            if airdrop:
                airdrop.is_tracked = False
                db.add(airdrop)

        await db.commit()

        # Invalidate cache
        await invalidate_tracked_airdrops_cache(current_user.id)

        return api_response(True, "Airdrop successfully removed from tracking", None)

    except Exception:
        await db.rollback()
        logger.exception("Error untracking airdrop")
        msg = "Untracking failed." if IS_PRODUCTION else "Error untracking airdrop"
        return api_response(False, msg, None)
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
        return api_response(
            True,
            "Tracked airdrops fetched (cache)",
            [item.model_dump(mode="json") for item in cached_list]
        )

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

    await set_cache(cache_key, json.dumps([d.model_dump() for d in response_data]), expire=3600)

    return api_response(True, "Tracked airdrops fetched", [item.model_dump(mode="json") for item in response_data])


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

    except Exception:
        logger.exception("Error fetching tracked airdrop count")
        msg = "Fetch failed." if IS_PRODUCTION else "Error fetching tracked airdrop count"
        return api_response(False, msg, None)



@app.post("/user/set_timer", response_model=GenericResponse)
@limiter.limit("10/minute")
async def set_timer(
    request: Request,
    payload: TimerRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
):
    try:
        airdrop_query = await db.execute(select(Submission).where(Submission.id == payload.submission_id))
        airdrop = airdrop_query.scalars().first()
        if not airdrop:
            return api_response(False, "Airdrop not found", None)

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
                "next_reminder_time": next_reminder_time.isoformat()
            }
        )

    except Exception:
        await db.rollback()
        logger.exception("Error setting timer")
        msg = "Set timer failed." if IS_PRODUCTION else "Error setting timer"
        return api_response(False, msg, None)


@app.patch("/user/settings", response_model=SettingsResponse)
@limiter.limit("10/minute")
async def update_settings(
    request: Request,
    payload: UserSettingsResponse,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    
):
    
    merged = {**DEFAULT_USER_SETTINGS, **(current_user.settings or {}), **payload.settings}
    current_user.settings = merged
    await db.commit()
    await db.refresh(current_user)
    return api_response(True, "Settings updated", {"user_id": current_user.id, "settings": merged})

@app.get("/user/{username}", response_model=GenericResponse)
async def read_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_session)
):
    try:
        user_result = await db.execute(select(User).where(User.username == username))
        user = user_result.scalars().first()

        if not user:
            return api_response(False, "User not found", None, status_code=404)

        return api_response(True, "User fetched successfully", UserScheme.from_orm(user))

    except Exception as e:
        logger.exception("Error fetching user by username")
        msg = "Failed to fetch user." if IS_PRODUCTION else f"Error: {str(e)}"
        return api_response(False, msg, None, status_code=500)


@app.post("/airdrop/upload_image", response_model=GenericResponse)
async def upload_airdrop_image(
    request: Request,
    file: UploadFile = File(...)
):
    try:
        # Validate file type
        allowed_extensions = {"jpg", "jpeg", "png", "gif"}
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in allowed_extensions:
            return api_response(False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}", None, 400)

        # Generate unique filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        safe_filename = f"airdrop_{timestamp}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Construct public URL
        image_url = f"{BASE_URL}/{UPLOAD_DIR}/{safe_filename}"

        return api_response(True, "Image uploaded successfully", {"image_url": image_url})

    except Exception as e:
        return api_response(False, f"Image upload failed: {str(e)}", None, status_code=500)


@app.post("/airdrop/post", response_model=GenericResponse)
@limiter.limit("10/minute")
async def post_airdrop(
    request: Request,
    payload: AirdropCreateSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    try:
        # Validate dates
        if payload.airdrop_end_date <= payload.airdrop_start_date:
            return api_response(False, "Airdrop end date must be after start date")

        # Ensure image_url is provided
        if not payload.image_url:
            return api_response(False, "Image is required for airdrop")

        # Check duplicates (title OR website)
        duplicate_check = await db.execute(
            select(Submission).where(
                (Submission.title == payload.title) | (Submission.website == str(payload.website))
            )
        )
        if duplicate_check.scalars().first():
            return api_response(False, "Airdrop with this title or website already exists")

        # Normalize datetimes (remove tzinfo)
        start_date = payload.airdrop_start_date.replace(tzinfo=None)
        end_date = payload.airdrop_end_date.replace(tzinfo=None)

        # Create new airdrop
        new_airdrop = Submission(
            image_url=str(payload.image_url),
            title=payload.title.strip(),
            chain=payload.chain,
            status=payload.status.value,
            website=str(payload.website),
            device_type=payload.device_type.value,
            funding=float(payload.funding) if payload.funding else None,
            cost_to_complete=int(payload.cost_to_complete) if payload.cost_to_complete else None,
            description=payload.description.strip(),
            category=payload.category.value,
            referral_link=payload.referral_link.strip(),
            token_symbol=payload.token_symbol.upper(),
            airdrop_start_date=start_date,
            airdrop_end_date=end_date,
            project_socials=payload.project_socials,
            submitted_at=datetime.utcnow(),
            submitted_by=current_user.id
        )

        db.add(new_airdrop)
        await db.commit()
        await db.refresh(new_airdrop)

        return api_response(
            True,
            "Airdrop submitted successfully. Pending admin verification.",
            {"airdrop": AirdropResponse.from_orm(new_airdrop).model_dump(mode="json")}
        )

    except IntegrityError:
        await db.rollback()
        return api_response(False, "Duplicate or invalid data")
    except Exception as e:
        await db.rollback()
        return api_response(False, f"Error: {str(e)}")

@app.get("/airdrop/list", response_model=List[AirdropResponse])
async def list_airdrops(
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    airdrops = await db.execute(
        select(Submission)
        .order_by(desc(Submission.airdrop_start_date))
        .offset(offset)
        .limit(limit)
    )
    airdrops = airdrops.scalars().all()
    return api_response(
        True,
        "Airdrops fetched",
        [a.model_dump(mode='json') for a in [AirdropResponse.from_orm(x) for x in airdrops]]
    )


@app.get("/airdrop/count", response_model=GenericResponse)
async def get_airdrop_count(
    db: AsyncSession = Depends(get_session)
):
    try:
        count_result = await db.execute(
            select(func.count()).select_from(Submission)
        )
        count = count_result.scalar()
        return api_response(True, "Airdrop count fetched", {"total_airdrops": count})   
    except Exception:
        logger.exception("Error fetching airdrop count")
        msg = "Fetch failed." if IS_PRODUCTION else "Error fetching airdrop count"
        return api_response(False, msg, None)


@app.post("/airdrop/{submission_id}/steps", response_model=GenericResponse)
async def add_airdrop_step(
    payload: AirdropStepCreate,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    submission_id: int = Path(..., description="The ID of the airdrop submission"),  # Path parameter

):
    try:
        result = await db.execute(select(Submission).where(Submission.id == submission_id))
        airdrop = result.scalar_one_or_none()
        if not airdrop:
            return api_response(False, "Airdrop not found", None, status_code=404)

        new_step = AirdropStep(
            submission_id=submission_id,
            step_number=payload.step_number,
            title=payload.title.strip(),
            instructions=[instr.model_dump() for instr in payload.instructions],
            image_url=payload.image_url
        )
        db.add(new_step)
        await db.commit()
        await db.refresh(new_step)

        return api_response(True, "Step added successfully", {
            "step": AirdropStepResponse.from_orm(new_step).model_dump(mode='json')
        })

    except Exception:
        await db.rollback()
        logger.exception("Error adding airdrop step")
        msg = "Step addition failed." if IS_PRODUCTION else "Error adding airdrop step"
        return api_response(False, msg, None, status_code=500)


@app.get("/airdrop/{airdrop_id}", response_model=AirdropResponse)
async def get_airdrop(
    airdrop_id: int,
    db: AsyncSession = Depends(get_session)
):
    airdrop = await db.execute(select(Submission).where(Submission.id == airdrop_id))
    airdrop = airdrop.scalars().first()
    if not airdrop:
        return api_response(False, "Airdrop not found", status_code=404)
    return api_response(True, "Airdrop fetched", {"airdrop": AirdropResponse.from_orm(airdrop).model_dump(mode="json")}) 


@app.get("/homepage_airdrops")
async def get_homepage_airdrops(
    limit: int = Query(5, gt=0, description="Number of airdrops to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_session)
):
    try:
        query = select(Submission)

        trending_q = (
            query.filter(Submission.rating_value < 50)
            .order_by(desc(Submission.rating_value))
            .limit(limit)
        )
        testnet_q = query.filter(Submission.category == "testnet").limit(limit)
        mining_q = query.filter(Submission.category == "mining").limit(limit)
        upcoming_q = (
            query.filter(Submission.airdrop_start_date > datetime.utcnow())
            .order_by(asc(Submission.airdrop_start_date))
            .limit(limit)
        )

        trending = (await db.execute(trending_q)).scalars().all()
        testnet = (await db.execute(testnet_q)).scalars().all()
        mining = (await db.execute(mining_q)).scalars().all()
        upcoming = (await db.execute(upcoming_q)).scalars().all()

        def serialize(airdrop):
            return {
                "id": airdrop.id,
                "title": airdrop.title,
                "rating": getattr(airdrop, "rating_value", None),
                "category": airdrop.category,
                "airdrop_start_date": (
                    airdrop.airdrop_start_date.isoformat()
                    if getattr(airdrop, "airdrop_start_date", None)
                    else None
                ),
                "image_url": getattr(airdrop, "image_url", None),
            }

        homepage_data = {
            "trending": [serialize(a) for a in trending],
            "testnet": [serialize(a) for a in testnet],
            "mining": [serialize(a) for a in mining],
            "upcoming": [serialize(a) for a in upcoming],
        }

        return api_response(True, "Homepage airdrops fetched successfully", homepage_data)

    except Exception as e:
        print("Error in /homepage_airdrops:", str(e))
        return api_response(False, f"Failed to fetch homepage airdrops: {str(e)}", None, status_code=500)