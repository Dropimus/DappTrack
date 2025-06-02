from pydantic import  BaseModel, Field, validator
from typing import Union, Optional, Dict, List, Any
from datetime import datetime

ALLOWED_CATEGORIES = {
    'standard',
    'retroactive',
    'socialfi',
    'gamefi',
    'mining',
    'testnet',
    'nft',
    'trading',
    'protocol'
}


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
    dapp_points: Optional[float] = None
    level: Optional[int] = None
    settings: Optional[Dict[str, Any]] = {}

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
    name: str
    chain: str
    status: str
    device_type: str
    funding: float
    description: str
    category: str
    external_airdrop_url: str  
    expected_token_ticker: Optional[str] = None
    airdrop_start_date: datetime
    airdrop_end_date: datetime
    project_socials: Optional[Dict[str, str]] = {} 
    image_url: str

    @validator("category")
    def validate_category(cls, v):
        v = v.lower().strip()
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(f"Invalid category: '{v}'. Must be one of {', '.join(ALLOWED_CATEGORIES)}.")
        return v

    class Config:
        from_attributes = True

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

class SettingsSchema(BaseModel):
    theme: Optional[str] = Field("light", description="UI theme, 'light' or 'dark'")
    notifications: Optional[bool] = Field(True, description="Enable in-app notifications")
    language: Optional[str] = Field("en", description="Locale code")
    airdrop_reminder: Optional[bool] = Field(True, description="Enable in-app reminders")
    task_completion_notification: Optional[bool] = Field(True, description="Enable in-app task completion notifications")

class SettingsUpdate(BaseModel):
    settings: Dict[str, Any]

class UserSettingsResponse(BaseModel):
    user_id: int
    settings: Dict[str, Any]

    class Config:
        from_attributes = True