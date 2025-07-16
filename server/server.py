from fastapi import (
    FastAPI, Depends, 
    WebSocket, WebSocketDisconnect,
    Body, Form, 
    HTTPException,Query,
     status, UploadFile, File
)
from websocket_manager import manager
from fastapi.responses import Response, JSONResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from models.models import (
    User, 
    Submission,
    AirdropStep,
    # AirdropRating,
    AirdropTracking,
    Timer
    )
from createDB import get_session, bootstrap_db
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import Annotated, List, Optional
from sqlalchemy.future import select
from sqlalchemy import asc, desc, func
from pydantic import BaseModel
import json
import secrets
from utils.config import get_settings
from cryptography.fernet import Fernet

from utils.utils import (
    create_access_token,
    create_refresh_token,
    generate_referral_code,
    authenticate_user,
    pwd_context,
    get_current_active_user,
    get_current_user_ws,
    decode_token,
    verify_password,
    get_password_hash,
    validate_password,
    record_points_transaction
)

from models.schemas import(
    Token, 
    TokenData, 
    UserScheme, 
    UserInDB, 
    UserUpdateSchema,
    ReferredUser, 
    UpdatePasswordSchema,
    AirdropCreateSchema,
    EncryptTokenData,
    UserResponse,
    AirdropTrackRequest,
    RatingRequestSchema,
    TimerRequest,
    SettingsUpdate,
    SettingsSchema,
    UserSettingsResponse
)
import boto3
import io
import os, shutil
import boto3
from botocore.client import Config
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR 
from botocore.exceptions import NoCredentialsError, ClientError

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from utils.redis import set_cache, get_cache, delete_cache, invalidate_tracked_airdrops_cache
from routers import hunters, bounties, ai_stub, submissions

# from pytonconnect import TonConnect




# s3 = boto3.client(
#     "s3",
#     endpoint_url=B2_ENDPOINT_URL,
#     aws_access_key_id=B2_KEY_ID,
#     aws_secret_access_key=B2_APPLICATION_KEY,
#     config=Config(
#         signature_version="s3v4",
#         request_checksum_calculation="WHEN_REQUIRED",
#         response_checksum_validation="WHEN_REQUIRED"
#     )
# )




#DEV Configuration for http

SECURE = False # In Production https -- set SECURE to True

# connector = TonConnect(manifest_url="https://yourdomain.com/static/tonconnect-manifest.json")
limiter = Limiter(key_func=get_remote_address)
settings = get_settings()

app = FastAPI(
    title='Dropimus API',
    description="api docs",
    version="1.0.0",
    root_path="/api"
    
) 

app.include_router(submissions.router, prefix="/submissions", tags=["Airdrop Submissions"])
# app.include_router(ai_stub.router, prefix="/ai", tags=["AI Stub"])
# app.include_router(hunters.router, prefix="/hunters", tags=["Hunter Pool"])
# app.include_router(bounties.router, prefix="/bounties", tags=["Bounties"])

app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

UPLOAD_DIR = "static/airdrop_image"
os.makedirs(UPLOAD_DIR, exist_ok=True)
# key = Fernet.generate_key()
# print(key)
key = settings.fernet_key
cipher = Fernet(key)

# Constants for points
SIGNUP_BONUS_POINTS = 5
AIRDROP_TRACKING_POINTS = 0.5
REFERRAL_BONUS_POINTS = 1

# @app.post('/')
# async def home():
#     return {' API'}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/signup")
@limiter.limit("5/minute") 
async def create_user(
    request: Request,
    username: str = Form(...), 
    full_name: str = Form(...),
    email: str = Form(...), 
    password: str = Form(...), 
    referral_code: str = Form(None),
    db: AsyncSession = Depends(get_session)
    ):
    validate_password(password)

    # Check for empty fields
    if not username or not full_name or not email or not password:
        raise HTTPException(status_code=400, detail="All fields are required")

    # Check if email already exists
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if user:
        raise HTTPException(status_code=400, detail="Email already exists")

    
    # check if usernname exists
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")


    hashed_password = pwd_context.hash(password)


    new_referral_code = generate_referral_code()
    print(f'New user referral code : {new_referral_code}')

    # Validate referral code if provided
    referred_by = None
    referrer = None
    if referral_code:
        result = await db.execute(select(User).where(User.referral_code == referral_code))
        referrer = result.scalars().first()     
        if not referrer:
            raise HTTPException(status_code=400, detail="Invalid referral code")

        await record_points_transaction(
                user_id=referrer.id,
                txn_type="referral_bonus",
                amount=REFERRAL_BONUS_POINTS,
                description=f"Referral Bonus for referring {username}",
                db=db
            )
        referred_by = referrer.id

    # Create user
    
    new_user = User(
        username=username.lower(),
        full_name=full_name,
        email=email,
        password_hash=hashed_password,
        referral_code=new_referral_code,
        referred_by=referred_by
    )

    db.add(new_user)
    await db.flush()

    try:
        if  new_user.id == 1:
            print(f'this is the user {new_user.id}')
            new_user.is_admin = True
            db.add(new_user)

        # if not new_user.has_signup_bonus():
        #     await record_points_transaction(
        #         user_id=new_user.id,
        #         txn_type="signup_bonus",
        #         amount=SIGNUP_BONUS_POINTS,
        #         description="Signup Bonus",
        #         db=db
        #     )
     

        await db.commit()
        await db.refresh(new_user)  
        return {"message": "User created successfully", 
                "user": new_user, 
                "honor_points": new_user.honor_points, 
                "referrer_points": referrer.honor_points if referrer else 0, 
               }

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")

    return {"message": "User created successfully", "user": new_user} 

@app.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    remember_me: bool = Form(False),
    response: Response = None,
    db: AsyncSession = Depends(get_session)
    ) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Token Handling    
    access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
    refresh_token_expires = timedelta(days=settings.refresh_token_expires_days if not remember_me else settings.remember_me_refresh_token_expires_days)


    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

    if remember_me:
        # print(f'THE REFRESH TOKEN {refresh_token}')
        response.set_cookie(key='refresh_token', value=refresh_token, secure=SECURE, httponly=True, max_age=int(refresh_token_expires.total_seconds()))

    return Token(access_token=access_token, token_type="bearer")


@app.post("/logout")
async def logout(response: Response, db: AsyncSession = Depends(get_session)):
    try:
        response.delete_cookie(key='refresh_token', secure=SECURE)
        response.delete_cookie(key='access_token', secure=SECURE)
        return {"message": "Successfully Logged Out"}
    except Exception as e: 
        raise HTTPException(status_code=500, detail="Error logging out")



@app.get("/user/me/", response_model=UserScheme)
async def read_users_me(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    ):
    print(f'The current User: {current_user}')
    return current_user

@app.get("/user/me/referrals", response_model=List[ReferredUser])
async def get_my_referrals(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
    ):
    
    # referral_code = current_user.referral_code  # get current user's code
    # stmt = select(User).where(User.referred_by == referral_code)
    # result = await db.execute(stmt)
    # referred_users = result.scalars().all()
    
    # print(f"Current user's referral code: {referral_code}")
    # print(f"Referred users: {[u.username for u in referred_users]}")

    # return referred_users


    user_id = current_user.id  # get current user's code f3936da8
    stmt = select(User).where(User.referred_by == user_id)
    result = await db.execute(stmt)
    referred_users = result.scalars().all()
    
    # print(f"Current user's referral code: {referral_code}")
    print(f"Referred users: {[u.username for u in referred_users]}")

    return referred_users

    # try:
    #     stmt = (
    #     select(User)
    #         .options(selectinload(User.referrals))
    #         .where(User.id == current_user.id)
    #     )
    #     result = await db.execute(stmt)
    #     user = result.scalars().first()

    #     if not orm_user:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail="User not found")
    #     referred_users = user.referrals

    #     return referred_users
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

@app.put("/user/me/edit", response_model=UserUpdateSchema)
async def update_user_info(
    updated_info: UserUpdateSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    
    ):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    for key, value in updated_info.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user

@app.put("/user/me/password")
async def update_user_password(
    password_data: UpdatePasswordSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
     
    ):
    user = db.query(User).filter(User.id == current_user.id).first()

    
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
   
    if password_data.new_password != password_data.confirm_new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match")
    
    user.password_hash = get_password_hash(password_data.new_password)
    
    await db.commit()
    await db.refresh(user)
    
    return {"message": "Password updated successfully"}


@app.get("/user/me/items/")
async def read_own_items(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    ):
    return [{"item_id": "Foo", "owner": current_user.username}]



@app.post("/token/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    refresh_token: str = None,
    ):
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not provided")
    
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
    new_access_token = create_access_token(data={"sub": payload["sub"]}, expires_delta=access_token_expires)
    
    return {"access_token": new_access_token, "token_type": "bearer"}


@app.post("/encrypt")
async def encrypt(tokens: EncryptTokenData):
    try:
        if tokens.access_token:
            encrypted_access_token = cipher.encrypt(tokens.access_token.encode()).decode()
        else:
            raise HTTPException(status_code=400, detail="Access token is required")
    
        encrypted_refresh_token = None
        if tokens.refresh_token:
            encrypted_refresh_token = cipher.encrypt(tokens.refresh_token.encode()).decode()
 
       

        return {
            "access_token": encrypted_access_token,
            "refresh_token": encrypted_refresh_token
        }

    except Exception as e:
        print(f"Error during encryption: {e}")
        raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")


@app.post("/decrypt")
async def decrypt_data(tokens: EncryptTokenData):
    try:
        if tokens.access_token:
            decrypted_access_token = cipher.decrypt(tokens.access_token.encode()).decode()

            # this checks if refresh token is provided and decrypts it
            decrypted_refresh_token = None
            if tokens.refresh_token:
                decrypted_refresh_token = cipher.decrypt(tokens.refresh_token.encode()).decode()

            response = {
                "access_token": decrypted_access_token
            }

            if decrypted_refresh_token:
                response["refresh_token"] = decrypted_refresh_token

            return response
        else:
            raise HTTPException(status_code=400, detail="Access token is required")

    except Exception as e:
        print(f'Error during decryption: {e}')
        raise HTTPException(status_code=500, detail="Decryption failed")




# For cloud uploads
# def upload_image(file_obj, object_name):
#     try:
#         s3.upload_fileobj(file_obj, B2_BUCKET_NAME, object_name)
#         print('IMAGE UPLOADED TO CLOUD')
#         return f"{B2_ENDPOINT_URL}/{B2_BUCKET_NAME}/{object_name}"
#     except NoCredentialsError:
#         raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="No credentials provided.")
#     except Exception as e:
#         raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def save_airdrop_image(submission_id: int, image: UploadFile):
    file_extension = image.filename.split(".")[-1]
    # Use the airdrop id as part of the filename
    filename = f"{submission_id}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return filename


@app.post('/post_airdrop')
async def create_airdrop(
    image: UploadFile = File(...),
    form_data: str = Form(...),
    
    db: AsyncSession = Depends(get_session)
    ):
    try:
        submission_data = json.loads(form_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in form_data"}

    print("Received submission_data:", submission_data)
    print("Image filename:", image.filename)

    submission_data["title"] = submission_data["title"].strip().title()
    submission_data["chain"] = submission_data["chain"].strip().lower()
    submission_data["status"] = submission_data["status"].strip().lower()
    submission_data["device"] = submission_data["device"].strip().lower()
    submission_data["category"] = submission_data["category"].strip().lower()
    submission_data["token_symbol"] = submission_data["token_symbol"].strip().upper()
    submission_data["referral_link"] = submission_data["referral_link"].strip().lower()


    
    # image_content = await image.read()
    # image_obj = io.BytesIO(image_content)
    # object_name = f"uploads/{image.filename}"  
    # image_url = upload_image(image_obj, object_name)

    # file_path = os.path.join(UPLOAD_DIR, image.filename)

    # with open(file_path, "wb") as buffer:
    #     shutil.copyfileobj(image.file, buffer)

    # image_url = f"/static/airdrop_image/{image.filename}"

    start_date = datetime.fromisoformat(submission_data["airdrop_start_date"])
    end_date = datetime.fromisoformat(submission_data["airdrop_end_date"])

    # ensure project_socials is a dict 
    if isinstance(submission_data["project_socials"], str):
        submission_data["project_socials"] = json.loads(submission_data["project_socials"])

    existing_submission_query = select(Submission).filter_by(referral_link=submission_data["referral_link"])
    existing_submission = await db.execute(existing_submission_query)
    existing_submission = existing_submission.scalars().first()

    image_url: str | None = None

    if existing_submission:

        try:
            filename = await save_airdrop_image(existing.id, image)
            image_url = f"/static/airdrop_image/{filename}"
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to upload image")
        # If airdrop exists, update the existing one (or return a message that it's a duplicate)
        existing_submission.status = submission_data["status"]
        existing_submission.funding = submission_data["funding"]
        existing_submission.description = submission_data["description"]
        existing_submission.category = submission_data["category"]
        existing_submission.project_socials = submission_data["project_socials"]
        
        existing_submission.airdrop_start_date = start_date
        existing_submission.airdrop_end_date = end_date
        if image_url:
            existing_submission.image_url = image_url

        try:
            # Commit the update
            await db.commit()
            print("Airdrop updated in DB.")
            return {"message": "Airdrop updated successfully", "id": existing_submission.id}
        except Exception as e:
            print(f"Error during commit or refresh: {e}")
            await db.rollback()
            return {"error": f"Failed to update airdrop: {str(e)}"}

    else:
        # If no existing airdrop, create a new one
        new_submission = Submission(
            title=submission_data["title"],
            chain=submission_data["chain"],
            status=submission_data["status"],
            device_type=submission_data["device"],
            funding=submission_data["funding"],
            cost_to_complete=submission_data["cost_to_complete"],
            description=submission_data["description"],
            category=submission_data["category"],
            referral_link=submission_data["referral_link"],
            token_symbol=submission_data["token_symbol"],
            airdrop_start_date=start_date,
            airdrop_end_date=end_date,
            project_socials=submission_data["project_socials"],  
            image_url=''
        )


        try:
            db.add(new_submission)
            await db.commit()
            print(f'Airdrop commited: {new_airdrop}')
            print("Airdrop committed to DB.")

            await db.refresh(new_submission)
            print(f"Airdrop ID after refresh: {new_submission.id}")
            filename = await save_airdrop_image(new_submission.id, image)
            image_url = f"/static/airdrop_image/{filename}"
            new_submission.image_url = image_url
            await db.commit()

            return {"message": "Airdrop stored successfully", "id": new_submission.id, 'image_url': new_submission.image_url}
        
        except Exception as e:
            print(f"Error during commit or refresh: {e}")
            await db.rollback()  
            return {"error": f"Failed to store airdrop: {str(e)}"}



@app.get("/airdrops")
async def get_airdrops(
    chain: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    name: Optional[str] = Query(None, description="Search by name"),
    sort_by: Optional[str] = Query(
        "airdrop_start_date", 
        description="Sort by either airdrop_start_date or created_at",
        regex="^(airdrop_start_date|created_at)$"
    ),
    order: Optional[str] = Query(
        "asc", 
        description="Sort order: asc or desc",
        regex="^(asc|desc)$"
    ),
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0),
    rating_gt: Optional[float] = Query(None, description="Minimum rating threshold"),
    db: AsyncSession = Depends(get_session)
    
    ):

    query = select(Submission)

    # filters 
    if chain:
        query = query.filter(Submission.chain.ilike(f"%{chain}%"))
    if status:
        query = query.filter(Submission.status.ilike(f"%{status}%"))
    if category:
        query = query.filter(Submission.category.ilike(f"%{category}%"))

    if name:
        # PSQL full text search functions:
        # convert the column to a tsvector and compare with plainto_tsquery.
        query = query.filter(
            func.to_tsvector('english', Submission.name)
                .match(func.plainto_tsquery('english', name))
        )
    
    # sorting
    sort_field = getattr(Submission, sort_by, None)
    if not sort_field:
        raise HTTPException(status_code=400, detail="Invalid sort field.")
    
    if order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))

    # pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    airdrops = result.scalars().all()

    response = [
        {
            "id": Submission.id,
            "title": Submission.title,
            "chain": Submission.chain,
            "status": Submission.status,
            "funding": Submission.funding,
            "category": Submission.category,
            "token_symbol": Submission.token_symbol,
            "referral_link": Submission.referral_link,
            "image_url": Submission.image_url,
            "airdrop_start_date": Submission.airdrop_start_date.isoformat() if Submission.airdrop_start_date else None,
            "airdrop_end_date": Submission.airdrop_end_date.isoformat() if Submission.airdrop_end_date else None,
            
            "created_at": Submission.created_at.isoformat() if hasattr(airdrop, "created_at") and Submission.created_at else None,
        }
        for airdrop in airdrops
    ]

    return {"airdrops": response}


@app.get("/airdrops/{submission_id}")
async def get_airdrop_by_id(submission_id: int, db: AsyncSession = Depends(get_session)):
    query = select(Submission).filter_by(id=submission_id)
    result = await db.execute(query)
    airdrop = result.scalars().first()

    if not airdrop:
        raise HTTPException(status_code=404, detail="Airdrop not found")

    response = {
        "id": Submission.id,
        "title": Submission.title,
        "chain": Submission.chain,
        "status": Submission.status,
        "rating_value": Submission.rating_value,
        "device_type": Submission.device_type,
        "cost_to_complete": Submission.cost_to_complete,
        "funding": Submission.funding,
        "category": Submission.category,
        "token_symbol": Submission.token_symbol,
        "referral_link": Submission.referral_link,
        "image_url": Submission.image_url,
        "airdrop_start_date": Submission.airdrop_start_date.isoformat() if Submission.airdrop_start_date else None,
        "airdrop_end_date": Submission.airdrop_end_date.isoformat() if Submission.airdrop_end_date else None,
        "created_at": Submission.created_at.isoformat() if hasattr(airdrop, "created_at") and Submission.created_at else None,
        
    }
    return response






@app.get("/homepage_airdrops")
async def get_homepage_airdrops(
    limit: int = Query(5, gt=0, description="Number of airdrops to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_session)
):
    print(f'Limit: {limit}, Offset: {offset}')

    # Optional: Print all entries for debug
    all_airdrops_result = await db.execute(select(Submission))
    all_airdrops = all_airdrops_result.scalars().all()
    print("All Airdrops:", all_airdrops)

    # Queries
    trending_airdrops_query = (
        select(Submission)
        .where(Submission.rating_value < 50)
        .order_by(desc(Submission.rating_value))
        .limit(limit)
    )

    testnet_airdrops_query = (
        select(Submission)
        .where(Submission.category == 'testnet')
        .limit(limit)
    )

    mining_airdrops_query = (
        select(Submission)
        .where(Submission.category == 'mining')
        .limit(limit)
    )

    upcoming_airdrops_query = (
        select(Submission)
        .where(Submission.airdrop_start_date > datetime.now())
        .order_by(asc(Submission.airdrop_start_date))
        .limit(limit)
    )

    # Execute the queries
    trending_result = await db.execute(trending_airdrops_query)
    trending_airdrops = trending_result.scalars().all()

    testnet_result = await db.execute(testnet_airdrops_query)
    testnet_airdrops = testnet_result.scalars().all()

    mining_result = await db.execute(mining_airdrops_query)
    mining_airdrops = mining_result.scalars().all()

    upcoming_result = await db.execute(upcoming_airdrops_query)
    upcoming_airdrops = upcoming_result.scalars().all()

    # Format the response properly using actual airdrop instances
    def format_airdrop(airdrop):
        return {
            "id": airdrop.id,
            "title": airdrop.title,
            "rating": airdrop.rating_value,
            "category": airdrop.category,
            "airdrop_start_date": airdrop.airdrop_start_date.isoformat() if airdrop.airdrop_start_date else None,
            "image_url": airdrop.image_url,
        }

    response = {
        "trending": [format_airdrop(a) for a in trending_airdrops],
        "testnet": [format_airdrop(a) for a in testnet_airdrops],
        "mining": [format_airdrop(a) for a in mining_airdrops],
        "upcoming": [format_airdrop(a) for a in upcoming_airdrops],
    }

    print(f'HOME PAGE AIRDROP RESPONSE: {response}')

    return response



# @app.post("/user/rate_airdrop")
# async def rate_airdrop(
#     rating_data: RatingRequestSchema,
#     current_user: Annotated[UserScheme, Depends(get_current_active_user)],

#     db: AsyncSession = Depends(get_session)
#     ):
#     submission_id = rating_data.submission_id
#     rating_value = rating_data.rating_value
#     user_id = current_user.id

#     # check if the rating value is valid (either 1 or -1)
#     if rating_value not in [1, -1]:
#         raise HTTPException(status_code=400, detail="Invalid rating value. Must be 1 (upvote) or -1 (downvote).")

#     # check if user is participating
#     participant = await db.execute(
#             select(AirdropTracking).filter_by(user_id=current_user.id, submission_id=submission_id)
#         )
#     print(participant.all())
#     if not participant:
#         raise HTTPException(status_code=403, detail="You must participate in the airdrop to rate it.")

#     # update the rating
#     rating = await db.execute(
#         select(AirdropRating).filter_by(user_id=user_id, submission_id=submission_id)
#     )
#     rating = rating.scalar_one_or_none()

#     if rating:
#         rating.rating_value = rating_value  # update existing rating
#     else:
#         rating = AirdropRating(user_id=user_id, submission_id=submission_id, rating_value=rating_value)
#         db.add(rating)

#     # Recalculate the total score by counting upvotes (+1) and downvotes (-1)
#     upvotes = await db.execute(
#         select(AirdropRating).filter_by(submission_id=submission_id, rating_value=1)
#     )
#     downvotes = await db.execute(
#         select(AirdropRating).filter_by(submission_id=submission_id, rating_value=-1)
#     )
#     upvote_count = len(upvotes.scalars().all())
#     downvote_count = len(downvotes.scalars().all())

#     total_score = upvote_count - downvote_count

#     # Update airdrop with the new total score
#     airdrop = await db.execute(select(Submission).filter_by(id=submission_id))
#     airdrop = Submission.scalar_one_or_none()
#     Submission.rating_value = total_score

#     db.add(Submission)
#     await db.commit()
    
#     return {"message": "Airdrop rated", "rating_value": total_score}



# Update completion percentage when a user completes a step
@app.post("/complete_airdrop_step")
async def complete_airdrop_step(
    submission_id: int, step_id: int, user_id: int, db: AsyncSession = Depends(get_session)
    ):
    try:
        # Find the airdrop participant record
        participant = await db.execute(
            select(AirdropParticipant).filter_by(user_id=user_id, submission_id=submission_id)
        )
        participant = participant.scalar_one_or_none()
        
        if not participant:
            raise HTTPException(status_code=404, detail="User is not participating in this airdrop")
        
        # Increment the completed steps
        participant.completed_steps += 1
        db.add(participant)
        await db.commit()

        # Recalculate the completion percentage
        airdrop = await db.execute(select(Submission).filter_by(id=submission_id))
        airdrop = Submission.scalar_one_or_none()
        
        if airdrop:
            total_steps = len(Submission.steps)  # Total steps in this airdrop
            completion_percent = (participant.completed_steps / total_steps) * 100
            Submission.completion_percent = int(completion_percent)
            db.add(Submission)
            await db.commit()

        return {"message": "Step completed", "completion_percent": Submission.completion_percent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing step: {str(e)}")




@app.post("/user/tracked/add")
@limiter.limit("5/minute") 
async def track_airdrop(
    request: Request,
    payload: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
    ):
    submission_id = payload.submission_id
    try:
        # Check if the airdrop already exists in the tracking list
        existing_tracking = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, submission_id=submission_id)
        )
        existing_tracking = existing_tracking.scalar_one_or_none()

        if existing_tracking:
            return {"message": "Airdrop is already being tracked"}

        # Add a new tracking record
        tracking = AirdropTracking(user_id=current_user.id, submission_id=submission_id)
        db.add(tracking)

        # Update the is_tracked field of the airdrop
        airdrop = await db.execute(select(Submission).filter_by(id=submission_id))
        airdrop = Submission.scalar_one_or_none()

        if not airdrop:
            raise HTTPException(status_code=404, detail="Airdrop not found")
        
        await record_points_transaction(
                user_id=current_user.id,
                txn_type="tracking_bonus",
                amount=AIRDROP_TRACKING_POINTS,
                description=f"Tracking Bonus for tracking airdrop",
                db=db
            )

        Submission.is_tracked = True
        db.add(Submission)

        # Commit changes
        await db.commit()
        
        await invalidate_tracked_airdrops_cache(current_user.id)

        return {"message": "Airdrop successfully added to tracking"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking airdrop: {str(e)}")


@app.post("/user/tracked/remove")
async def untrack_airdrop(
    payload: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
    ):
    submission_id = payload.submission_id
    try:
        # Find the tracking record
        tracking = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, submission_id=submission_id)
        )
        tracking = tracking.scalar_one_or_none()

        if not tracking:
            raise HTTPException(status_code=404, detail="Airdrop is not being tracked")

        # Remove the tracking record
        await db.delete(tracking)

        # Check if any other users are tracking the airdrop
        other_trackers = await db.execute(
            select(AirdropTracking).filter_by(submission_id=submission_id)
        )
        other_trackers = other_trackers.scalars().all()

        # If no other users are tracking the airdrop, update the `is_tracked` field
        if not other_trackers:
            airdrop = await db.execute(select(Submission).filter_by(id=submission_id))
            airdrop = Submission.scalar_one_or_none()

            if airdrop:
                Submission.is_tracked = False
                db.add(Submission)

        # Commit changes
        await db.commit()

         # Invalidate Redis cache for this user
        await invalidate_tracked_airdrops_cache(current_user.id)

        return {"message": "Airdrop successfully removed from tracking"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error untracking airdrop: {str(e)}")



# @app.get("/user/tracked")
# async def get_tracked_airdrops(
#     current_user: Annotated[UserScheme, Depends(get_current_active_user)],
#     db: AsyncSession = Depends(get_session)
#     ):
#     try:
#         print('no')
#         # Query the tracked airdrops for the current user
#         tracked_airdrops = await db.execute(
#             select(Submission).join(AirdropTracking).filter(AirdropTracking.user_id == current_user.id)
#         )
#         tracked_airdrops = tracked_airdrops.scalars().all()
#         return {"tracked_airdrops": tracked_airdrops}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching tracked airdrops: {str(e)}")

@app.get("/user/tracked")
async def get_tracked_airdrops(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    cache_key = f"user:{current_user.id}:tracked_airdrops"

    try:
        cached_data = await get_cache(cache_key)
        if cached_data:
            return {"tracked_airdrops": json.loads(cached_data)}

        # fallback to DB query
        tracked_airdrops = await db.execute(
            select(Submission).join(AirdropTracking).filter(AirdropTracking.user_id == current_user.id)
        )
        tracked_airdrops = tracked_airdrops.scalars().all()

        # serialize and cache result
        serialized = [Submission.__dict__ for airdrop in tracked_airdrops]
        for item in serialized:
            item.pop('_sa_instance_state', None)  # Remove SQLAlchemy internal field

        await set_cache(cache_key, json.dumps(serialized), expire=3600)

        return {"tracked_airdrops": serialized}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tracked airdrops: {str(e)}")


        
@app.get("/user/tracked/count")
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
        return {"total_tracked": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tracked airdrop count: {str(e)}")




@app.post("/user/set_timer")
async def set_timer(
    timer: TimerRequest, current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)):

    try:
        airdrop_query = await db.execute(select(Submission).where(Submission.id == timer.submission_id))
        airdrop = airdrop_query.scalars().first()
        if not airdrop:
            raise HTTPException(status_code=404, detail="Airdrop not found")

        next_reminder_time = datetime.utcnow() + timedelta(seconds=timer.total_seconds)

        new_timer = Timer(
            user_id=current_user.id,
            submission_id=timer.submission_id,
            reminder_interval=timer.total_seconds,
            next_reminder_time=next_reminder_time,
            is_active=True
        )
        db.add(new_timer)
        await db.commit()
        await db.refresh(new_timer)
        return {
            "message": "Timer set successfully",
            "timer_id": new_timer.id,
            "next_reminder_time": next_reminder_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking airdrop: {str(e)}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: Annotated[UserScheme, Depends(get_current_user_ws)],):
    
    await manager.connect(websocket, current_user.id)
    
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
    
@app.get("/send-broadcast")
async def send_broadcast():
    try:
        await manager.broadcast("Test broadcast")
        return {"status": "broadcast sent"}
    except Exception as e:
        return {"status": f"error: {str(e)}"}


# @app.get("/user/settings", response_model=UserSettingsResponse)
# async def get_settings(current_user: Annotated[UserScheme, Depends(get_current_active_user)]):
#     # Merge defaults with stored settings
#     defaults = SettingsSchema().dict()
#     merged = {**defaults, **current_user.settings}
#     return UserSettingsResponse(user_id=current_user.id, settings=merged)

@app.patch("/user/settings", response_model=UserSettingsResponse)
async def update_settings(
    payload: SettingsUpdate,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
):
    for key, value in payload.settings.items():
        current_user.settings[key] = value
    await db.commit()
    await db.refresh(current_user)
    
    # Merge defaults for response
    defaults = SettingsSchema().dict()
    merged = {**defaults, **current_user.settings}
    return UserSettingsResponse(user_id=current_user.id, settings=merged)


############### WALLET CONNECT ########################

# @app.get("/wallet/restore")
# async def restore_wallet(
#     current_user: Annotated[UserScheme, Depends(get_current_active_user)],
#     db: AsyncSession = Depends(get_session)
# ):
#     is_connected = await connector.restore_connection()
#     return {"is_connected": is_connected}


# @app.get("/wallets")
# async def get_wallets(
#     current_user: Annotated[UserScheme, Depends(get_current_active_user)],
#     db: AsyncSession = Depends(get_session)
# ):
#     wallets_list = connector.get_wallets()
#     return {"wallets": wallets_list}

# @app.get("/wallet/connect")
# async def connect_wallet(wallet_index: int, current_user: Annotated[UserScheme, Depends(get_current_active_user)],
#     db: AsyncSession = Depends(get_session)):
#     wallets_list = connector.get_wallets()
#     if wallet_index >= len(wallets_list):
#         return {"error": "Invalid wallet index"}
    
#     generated_url = await connector.connect(wallets_list[wallet_index])
#     return {"connect_url": generated_url}

# @app.post("/wallet/transaction")
# async def send_transaction(transaction: dict, current_user: Annotated[UserScheme, Depends(get_current_active_user)],
#     db: AsyncSession = Depends(get_session)):
#     try:
#         result = await connector.send_transaction(transaction)
#         return {"message": "Transaction successful", "result": result}
#     except Exception as e:
#         if isinstance(e, UserRejectsError):
#             return {"error": "Transaction rejected by the user"}
#         return {"error": str(e)}



########################## ADMIN ########################

@app.get("/users", response_model=List[UserScheme])
async def get_all_users(db: AsyncSession = Depends(get_session)):
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return users

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

# @app.post("/airdrops/upload", response_model=AirdropCreate)
# async def upload_airdrop(airdrop: AirdropCreate, db: AsyncSession = Depends(get_session)):
#     new_airdrop = Airdrop(**Submission.dict())
#     db.add(new_submission)
#     await db.commit()
#     await db.refresh(new_submission)
#     return new_airdrop

    
# this works when using curl 



# curl -X POST "http://127.0.0.1:8000/signup" \
# -H "Content-Type: application/x-www-form-urlencoded" \
# --data-urlencode "username=new_user" \
# --data-urlencode "full_name=New User" \
# --data-urlencode "referral_code=cb5675f8"
# --data-urlencode "email=newuser@example.com" \
# --data-urlencode "password=SecurePassword123!"


# curl -X POST http://localhost:8000/signup -F "username=exampleuser1" -F "full_name=Example User" -F "email=example1@example.com" -F "password=SecurePassword123!" -F "referral_code=cb5675f8"



# curl -X POST "http://127.0.0.1:8000/login" \
# -H "Content-Type: application/x-www-form-urlencoded" \
# --data-urlencode "username=new_user" \
# --data-urlencode "password=SecurePassword123!" \
# --data-urlencode "remember_me=true"





# curl -X POST "http://127.0.0.1:8000/post_airdrop" \
# -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyMjc4MH0.znGkjWZuVKYTQ00b-9t421GkTjcyzTeIy_nlVSx07Y4" \
# -H "Content-Type: multipart/form-data" \
# -F "file=@/home/ukov/DappTrack/assets/5983122776472535666.jpg" \
# -F 'airdrop={"image_url":"/home/ukov/DappTrack/assets/5983122776472535666.jpg","name":"Example Airdrop","description":"An example airdrop description","upload_date":"2024-12-26T12:00:00","status":"running","category":"Crypto","rating_value":4.5,"project_socials":{"twitter":"https://twitter.com/example","discord":"https://discord.gg/example"},"amount_raised":50000,"completion_percent":80,"airdrop_start_date":"2024-12-27T12:00:00","airdrop_end_date":"2025-01-01T12:00:00","is_tracked":true}'


# curl -X POST "http://127.0.0.1:8000/untrack_airdrop" \
# -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyNjIwNH0.62losUk891C4AphvbP5qwWFwUe1vSdkHlM4YQRs2NEg" \
# -H "Content-Type: application/json" \
# -d '{"submission_id": 1}'


# curl -X GET "http://127.0.0.1:8000/tracked_airdrops" \
# -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyNjIwNH0.62losUk891C4AphvbP5qwWFwUe1vSdkHlM4YQRs2NEg" \
# -H "Content-Type: application/json"


# curl -X POST "http://127.0.0.1:8000/rate_airdrop" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyODQyNH0.lGYfUX7xuT_a02xWX8-8wdCKh6sRPhqtSd0H2LmNRj4" -H "Content-Type: application/json" -d '{
#   "submission_id": 1,
#   "rating_value": 1
# }'

