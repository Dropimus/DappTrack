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

class ProjectSocials(BaseModel):
    twitter: Optional[str]
    telegram: Optional[str]
    discord: Optional[str]

class AirdropCreateSchema(BaseModel):
    id: int
    image_url: Optional[str]
    name: str
    chain: str
    status: str
    device: str
    funding: float
    description: Optional[str]
    category: str
    external_airdrop_url: Optional[str]
    expected_token_ticker: Optional[str]
    airdrop_start_date: datetime
    airdrop_end_date: datetime
    project_socials: ProjectSocials
 

    @validator("airdrop_start_date", "airdrop_end_date", pre=True)
    def parse_dates(cls, value):
        if isinstance(value, str):
            return datetime.strptime(cleaned, "%Y-%m-%d %I:%M %p")
        return value

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %I:%M %p")
        }
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

