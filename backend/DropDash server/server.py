from fastapi import FastAPI, Depends, Body, Form, HTTPException,Query, status, UploadFile, File
from fastapi.responses import Response, JSONResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from models import (
    User, 
    Airdrop,
    AirdropStep,
    AirdropRating,
    AirdropTracking,
    Timer
    )
from createDB import get_session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import Annotated, List
from sqlalchemy.future import select
from pydantic import BaseModel
import json
import secrets
from config import settings
from cryptography.fernet import Fernet

from utils import (
    create_access_token,
    create_refresh_token,
    authenticate_user,
    pwd_context,
    get_current_active_user,
    decode_token,
    verify_password,
    get_password_hash,
    validate_password
)

from schemas import(
    Token, 
    TokenData, 
    UserScheme, 
    UserInDB, 
    UserUpdateSchema,
    ReferredUser, 
    UpdatePasswordSchema,
    AirdropCreate,
    EncryptTokenData,
    UserResponse,
    AirdropTrackRequest,
    RatingRequestSchema,
    TimerRequest
)

# from pytonconnect import TonConnect

#DEV Configuration for http

SECURE = False # In Production https -- set SECURE to True

# connector = TonConnect(manifest_url="https://yourdomain.com/static/tonconnect-manifest.json")

app = FastAPI(
    title='DropDash API',
    description="DropDash: Airdrop Tracker.",
    version="1.0.0",
    contact={
        'name': 'Victor Uko'
    } 
) 

app.mount("/static", StaticFiles(directory="static"), name="static")


key = Fernet.generate_key()
cipher = Fernet(key)


# @app.post('/')
# async def home():
#     return {' API'}

def generate_referral_code():
    return secrets.token_hex(4)



@app.post("/signup")
async def create_user(
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
    if referral_code:
        result = await db.execute(select(User).where(User.referral_code == referral_code))
        referrer = result.scalars().first()
        if not referrer:
            raise HTTPException(status_code=400, detail="Invalid referral code")
        referred_by = referral_code

    # Create user
    
    new_user = User(
        username=username,
        full_name=full_name,
        email=email,
        password_hash=hashed_password,
        referral_code=new_referral_code,
        referred_by=referred_by
    )

    db.add(new_user)
    db.flush()

    try:
        if  new_user.id == 3:
            new_user.is_admin = True
            db.add(new_user)
        await db.commit() 
        await db.refresh(new_user)  # Refresh the instance to get the new data
        return {"message": "User created successfully", "user": new_user}
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


@app.post("/post_airdrop")
async def create_airdrop(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)], 
    airdrop: str = Form(...),
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_session)):
    try:
        

        airdrop_dict = json.loads(airdrop)

        airdrop_data = AirdropCreate(**airdrop_dict)
        print("Received airdrop:", airdrop_data.dict())
        print("Uploaded file:", file.filename)

        file_location = f"uploads/{file.filename}"  
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        new_airdrop = Airdrop()
        
        
        airdrop_data.image_url = file_location
        
        # update the new_airdrop object dynamically from airdrop fields
        for key, value in airdrop_data.dict(exclude_unset=True).items():
            setattr(new_airdrop, key, value)
        
        db.add(new_airdrop)
        await db.commit()
        await db.refresh(new_airdrop)

        return {"message": "Airdrop added successfully", "airdrop": new_airdrop}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating airdrop: {str(e)}")




@app.get("/get_airdrops")
async def get_airdrops(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    limit: int = Query(100, le=1000), 
    offset: int = Query(0), 
    category: str = Query(None, enum=[
        "Testnets", "Retroactive", "Mining", "NFT Airdrops",
        "SocialFi", "GameFi", "General Airdrop", "Promotional Airdrop", "Others"
    ]), 
    sort_by: str = Query("rating", enum=["rating", "newest", "oldest"]), 

    db: AsyncSession = Depends(get_session)
    ):
    print(f'the current user {current_user}')
    query = select(Airdrop.id, Airdrop.name, Airdrop.image_url, Airdrop.rating_value, Airdrop.category)
    
    if category:
        query = query.filter(Airdrop.category == category)
    

    if sort_by == "rating":
        query = query.order_by(desc(Airdrop.rating_value))
    elif sort_by == "newest":
        query = query.order_by(desc(Airdrop.start_date))
    elif sort_by == "oldest":
        query = query.order_by(Airdrop.start_date)
    
    query = query.offset(offset).limit(limit)

    # Execute the query asynchronously
    result = await db.execute(query)
    airdrops = result.fetchall()  
    
    return {"airdrops": airdrops}


@app.get("/users/me/", response_model=UserScheme)
async def read_users_me(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    ):
    print(f'The current User: {current_user}')
    return current_user

@app.get("/users/me/referrals", response_model=List[ReferredUser])
async def get_my_referrals(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
    ):
    
    referral_code = current_user.referral_code  # get current user's code
    stmt = select(User).where(User.referred_by == referral_code)
    result = await db.execute(stmt)
    referred_users = result.scalars().all()
    
    print(f"Current user's referral code: {referral_code}")
    print(f"Referred users: {[u.username for u in referred_users]}")

    return referred_users

@app.put("/users/me/edit", response_model=UserUpdateSchema)
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

@app.put("/users/me/password")
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


@app.get("/users/me/items/")
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
 
        print(f"Encrypted access token: {encrypted_access_token}")

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



@app.post("/rate_airdrop")
async def rate_airdrop(
    rating_data: RatingRequestSchema,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],

    db: AsyncSession = Depends(get_session)
    ):
    airdrop_id = rating_data.airdrop_id
    rating_value = rating_data.rating_value
    user_id = current_user.id

    # Check if the rating value is valid (either 1 or -1)
    if rating_value not in [1, -1]:
        raise HTTPException(status_code=400, detail="Invalid rating value. Must be 1 (upvote) or -1 (downvote).")

    # Check if user is participating
    participant = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, airdrop_id=airdrop_id)
        )
    print(participant.all())
    if not participant:
        raise HTTPException(status_code=403, detail="You must participate in the airdrop to rate it.")

    # Add or update the rating
    rating = await db.execute(
        select(AirdropRating).filter_by(user_id=user_id, airdrop_id=airdrop_id)
    )
    rating = rating.scalar_one_or_none()

    if rating:
        rating.rating_value = rating_value  # Update existing rating
    else:
        rating = AirdropRating(user_id=user_id, airdrop_id=airdrop_id, rating_value=rating_value)
        db.add(rating)

    # Recalculate the total score by counting upvotes (+1) and downvotes (-1)
    upvotes = await db.execute(
        select(AirdropRating).filter_by(airdrop_id=airdrop_id, rating_value=1)
    )
    downvotes = await db.execute(
        select(AirdropRating).filter_by(airdrop_id=airdrop_id, rating_value=-1)
    )
    upvote_count = len(upvotes.scalars().all())
    downvote_count = len(downvotes.scalars().all())

    total_score = upvote_count - downvote_count

    # Update airdrop with the new total score
    airdrop = await db.execute(select(Airdrop).filter_by(id=airdrop_id))
    airdrop = airdrop.scalar_one_or_none()
    airdrop.rating_value = total_score

    db.add(airdrop)
    await db.commit()
    
    return {"message": "Airdrop rated", "rating_value": total_score}



# Update completion percentage when a user completes a step
@app.post("/complete_airdrop_step")
async def complete_airdrop_step(
    airdrop_id: int, step_id: int, user_id: int, db: AsyncSession = Depends(get_session)
    ):
    try:
        # Find the airdrop participant record
        participant = await db.execute(
            select(AirdropParticipant).filter_by(user_id=user_id, airdrop_id=airdrop_id)
        )
        participant = participant.scalar_one_or_none()
        
        if not participant:
            raise HTTPException(status_code=404, detail="User is not participating in this airdrop")
        
        # Increment the completed steps
        participant.completed_steps += 1
        db.add(participant)
        await db.commit()

        # Recalculate the completion percentage
        airdrop = await db.execute(select(Airdrop).filter_by(id=airdrop_id))
        airdrop = airdrop.scalar_one_or_none()
        
        if airdrop:
            total_steps = len(airdrop.steps)  # Total steps in this airdrop
            completion_percent = (participant.completed_steps / total_steps) * 100
            airdrop.completion_percent = int(completion_percent)
            db.add(airdrop)
            await db.commit()

        return {"message": "Step completed", "completion_percent": airdrop.completion_percent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing step: {str(e)}")



@app.post("/track_airdrop")
async def track_airdrop(
    request: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
    ):
    airdrop_id = request.airdrop_id
    try:
        # Check if the airdrop already exists in the tracking list
        existing_tracking = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, airdrop_id=airdrop_id)
        )
        existing_tracking = existing_tracking.scalar_one_or_none()

        if existing_tracking:
            return {"message": "Airdrop is already being tracked"}

        # Add a new tracking record
        tracking = AirdropTracking(user_id=current_user.id, airdrop_id=airdrop_id)
        db.add(tracking)

        # Update the is_tracked field of the airdrop
        airdrop = await db.execute(select(Airdrop).filter_by(id=airdrop_id))
        airdrop = airdrop.scalar_one_or_none()

        if not airdrop:
            raise HTTPException(status_code=404, detail="Airdrop not found")

        airdrop.is_tracked = True
        db.add(airdrop)

        # Commit changes
        await db.commit()
        return {"message": "Airdrop successfully added to tracking"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking airdrop: {str(e)}")


@app.post("/untrack_airdrop")
async def untrack_airdrop(
    request: AirdropTrackRequest,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
    ):
    airdrop_id = request.airdrop_id
    try:
        # Find the tracking record
        tracking = await db.execute(
            select(AirdropTracking).filter_by(user_id=current_user.id, airdrop_id=airdrop_id)
        )
        tracking = tracking.scalar_one_or_none()

        if not tracking:
            raise HTTPException(status_code=404, detail="Airdrop is not being tracked")

        # Remove the tracking record
        await db.delete(tracking)

        # Check if any other users are tracking the airdrop
        other_trackers = await db.execute(
            select(AirdropTracking).filter_by(airdrop_id=airdrop_id)
        )
        other_trackers = other_trackers.scalars().all()

        # If no other users are tracking the airdrop, update the `is_tracked` field
        if not other_trackers:
            airdrop = await db.execute(select(Airdrop).filter_by(id=airdrop_id))
            airdrop = airdrop.scalar_one_or_none()

            if airdrop:
                airdrop.is_tracked = False
                db.add(airdrop)

        # Commit changes
        await db.commit()
        return {"message": "Airdrop successfully removed from tracking"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error untracking airdrop: {str(e)}")



@app.get("/tracked_airdrops")
async def get_tracked_airdrops(
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
    ):
    try:
        print('no')
        # Query the tracked airdrops for the current user
        tracked_airdrops = await db.execute(
            select(Airdrop).join(AirdropTracking).filter(AirdropTracking.user_id == current_user.id)
        )
        tracked_airdrops = tracked_airdrops.scalars().all()
        return {"tracked_airdrops": tracked_airdrops}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tracked airdrops: {str(e)}")



@app.post("/set_timer")
async def set_timer(
    timer: TimerRequest, current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)):

    try:
        airdrop_query = await db.execute(select(Airdrop).where(Airdrop.id == timer.airdrop_id))
        airdrop = airdrop_query.scalars().first()
        if not airdrop:
            raise HTTPException(status_code=404, detail="Airdrop not found")

        next_reminder_time = datetime.utcnow() + timedelta(seconds=timer.total_seconds)

        new_timer = Timer(
            user_id=current_user.id,
            airdrop_id=timer.airdrop_id,
            reminder_interval=timer.total_seconds,
            next_reminder_time=next_reminder_time,
            is_active=True
        )
        db.add(new_timer)
        await db.commit()
        await db.refresh(mew_timer)
        return {
            "message": "Timer set successfully",
            "timer_id": new_timer.id,
            "next_reminder_time": next_reminder_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking airdrop: {str(e)}")



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

@app.post("/airdrops/upload", response_model=AirdropCreate)
async def upload_airdrop(airdrop: AirdropCreate, db: AsyncSession = Depends(get_session)):
    new_airdrop = Airdrop(**airdrop.dict())
    db.add(new_airdrop)
    await db.commit()
    await db.refresh(new_airdrop)
    return new_airdrop

    
# this works when using curl to post data



# curl -X POST "http://127.0.0.1:8000/signup" \
# -H "Content-Type: application/x-www-form-urlencoded" \
# --data-urlencode "username=new_user" \
# --data-urlencode "full_name=New User" \
# --data-urlencode "email=newuser@example.com" \
# --data-urlencode "password=SecurePassword123!"

# curl -X POST "http://127.0.0.1:8000/login" \
# -H "Content-Type: application/x-www-form-urlencoded" \
# --data-urlencode "username=new_user" \
# --data-urlencode "password=SecurePassword123!" \
# --data-urlencode "remember_me=true"





# curl -X POST "http://127.0.0.1:8000/post_airdrop" \
# -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyMjc4MH0.znGkjWZuVKYTQ00b-9t421GkTjcyzTeIy_nlVSx07Y4" \
# -H "Content-Type: multipart/form-data" \
# -F "file=@/home/ukov/DropDash/assets/5983122776472535666.jpg" \
# -F 'airdrop={"image_url":"/home/ukov/DropDash/assets/5983122776472535666.jpg","name":"Example Airdrop","description":"An example airdrop description","upload_date":"2024-12-26T12:00:00","status":"running","category":"Crypto","rating_value":4.5,"project_socials":{"twitter":"https://twitter.com/example","discord":"https://discord.gg/example"},"amount_raised":50000,"completion_percent":80,"airdrop_start_date":"2024-12-27T12:00:00","airdrop_end_date":"2025-01-01T12:00:00","is_tracked":true}'


# curl -X POST "http://127.0.0.1:8000/untrack_airdrop" \
# -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyNjIwNH0.62losUk891C4AphvbP5qwWFwUe1vSdkHlM4YQRs2NEg" \
# -H "Content-Type: application/json" \
# -d '{"airdrop_id": 1}'


# curl -X GET "http://127.0.0.1:8000/tracked_airdrops" \
# -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyNjIwNH0.62losUk891C4AphvbP5qwWFwUe1vSdkHlM4YQRs2NEg" \
# -H "Content-Type: application/json"


# curl -X POST "http://127.0.0.1:8000/rate_airdrop" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTczNTQyODQyNH0.lGYfUX7xuT_a02xWX8-8wdCKh6sRPhqtSd0H2LmNRj4" -H "Content-Type: application/json" -d '{
#   "airdrop_id": 1,
#   "rating_value": 1
# }'

