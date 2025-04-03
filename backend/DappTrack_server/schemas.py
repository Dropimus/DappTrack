from pydantic import  BaseModel, Field, validator
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


class AirdropCreateSchema(BaseModel):
    image_url: str
    name: str
    chain: str
    status: str 
    device: Optional[str] = None
    funding: Optional[float] = None
    description: str
    category: str
    external_airdrop_url: str
    upload_date: datetime = datetime.now()
    rating_value: Optional[float] = 0.0
    project_socials: Optional[Dict[str, str]] = None
    expected_token_ticker: Optional[str] = None
    airdrop_start_date: Optional[str] = None
    airdrop_end_date: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    @validator("airdrop_start_date", "airdrop_end_date", pre=True)
    def clean_and_format_date(cls, value):
        if value:
            date_part = " ".join(value.split()[1:])  # Remove 'start' or 'end'
            return datetime.strptime(date_part, "%Y-%m-%d %I:%M %p").isoformat()
        return None 

class AirdropSteps(BaseModel):
    airdrop_id: int
    airdrop_steps: str

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