from pydantic import  BaseModel, Field
from typing import Union, Optional, Dict, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    
class ReferredUser(BaseModel):
    id: int
    username: str
    full_name: str

    class Config:
        from_attributes = True



class UserScheme(BaseModel):
    id: int
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    is_admin: Union[bool, None] = None
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    disabled: Union[bool, None] = None

    class Config:
        from_attributes = True

class UserInDB(UserScheme):
    hashed_password: str

class UserUpdateSchema(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None

    class Config:
        from_attributes = True

class UpdatePasswordSchema(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str


class AirdropCreate(BaseModel):
    image_url: str
    name: str
    description: Optional[str] = None
    upload_date: datetime
    status: str = Field(default="Active", description="Status of the airdrop")
    category: Optional[str] = None
    rating_value: Optional[float] = 0.0
    project_socials: Optional[Dict[str, str]] = None
    amount_raised: Optional[float] = None
    completion_percent: int
    airdrop_start_date: datetime
    airdrop_end_date: datetime
    is_tracked: bool = False



class EncryptTokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: str

    class Config:
        from_attributes = True

class AirdropTrackRequest(BaseModel):
    airdrop_id: int

class RatingRequestSchema(BaseModel):
    airdrop_id: int
    rating_value: int 

class TimerRequest(BaseModel):
    airdrop_id: int
    total_seconds: int