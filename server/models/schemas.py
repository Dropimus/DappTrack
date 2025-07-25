from pydantic import  BaseModel, Field, validator, HttpUrl
from typing import Union, Optional, Dict, List, Any
from datetime import datetime, date

ALLOWED_CATEGORIES = {
    'standard',
    'retroactive',
    'socialfi',
    'infofi',
    'gamefi',
    'mining',
    'testnet',
    'nft',
    'trading',
    'protocol',
    'staking',
    'guild',
    'ai'
}


ALLOWED_DEVICE_TYPES = {"desktop", "mobile", "desktop & mobile"}

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
    honor_points: Optional[float] = None
    title: Union[str, None] = None
    settings: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True

class NotificationRequest(BaseModel):
    token: str
    title: str
    body: str

class FirebaseTokenRequest(BaseModel):
    id_token: str

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


class RatingRequestSchema(BaseModel):
    airdrop_id: int
    rating_value: int 

class TimerRequest(BaseModel):
    submission_id: int
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

############################# Airdrop Validation #########################

class VoteCreate(BaseModel):
    vote: str = Field(..., pattern="^(approve|reject)$")

class AirdropTrackRequest(BaseModel):
    submission_id: int

class AirdropCreateSchema(BaseModel):
    id: int
    title: str
    chain: str
    status: str
    device_type: str
    funding: float
    description: str
    category: str
    referral_link: str  
    token_symbol: Optional[str] = None
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


class AirdropStep(BaseModel):
    description: str = Field(..., example="Follow on Twitter")
    url: Optional[HttpUrl] = Field(None, example="https://twitter.com/project")
    required: bool = True


class EligibilityCriterion(BaseModel):
    description: str = Field(..., example="Hold ≥10 SOL")
    required: bool = True

class SimpleAirdropSubmissionCreate(BaseModel):
    title: str = Field(..., example="splashit")
    description: str = Field(..., example="splashit is an airdrop on sui chain.")
    chain: str = Field(..., example="Sui")
    website: HttpUrl = Field(..., example="https://splashit.com")
    token_symbol: str = Field(..., example="SPLASH")
    social_links: List[HttpUrl] = Field(default=[], example=["https://twitter.com/splashit", "https://t.me/splashit"])
    category: str = Field(..., example="standard")
    device_type: str = Field(default="desktop & mobile", example="desktop")

    @validator('category')
    def validate_category(cls, v):
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}")
        return v

    @validator('device_type')
    def validate_device_type(cls, v):
        if v not in ALLOWED_DEVICE_TYPES:
            raise ValueError(f"device_type must be one of: {', '.join(ALLOWED_DEVICE_TYPES)}")
        return v


class AdvancedAirdropSubmissionCreate(SimpleAirdropSubmissionCreate):
    snapshot_date: Optional[date] = Field(None, example="2025-07-15")
    max_reward: Optional[float] = Field(None, description="Max tokens per user, if known")
    eligibility_summary: Optional[str] = Field(None, example="Must hold ≥10 SOL at snapshot and complete swaps.")
    eligibility_criteria: List[EligibilityCriterion] = Field(default=[])
    steps: List[AirdropStep] = Field(default=[])


class SubmissionRead(BaseModel):
    id: int
    title: str
    description: str
    chain: str
    website: HttpUrl
    token_symbol: str
    social_links: List[HttpUrl]
    category: str
    device_type: str

    snapshot_date: Optional[date]
    max_reward: Optional[float]
    eligibility_summary: Optional[str]
    eligibility_criteria: List[EligibilityCriterion]
    steps: List[AirdropStep]

    class Config:
        from_attributes = True

class TrackedAirdropSchema(BaseModel):
    id: int
    title: str
    image_url: str
    status: Optional[str]
    task_progress: Optional[float]
    duration: Optional[str] = None

    @classmethod
    def from_orm_with_duration(cls, airdrop, task_progress: float):
        # Safely calculate duration
        if airdrop.airdrop_start_date and airdrop.airdrop_end_date:
            duration_days = (airdrop.airdrop_end_date - airdrop.airdrop_start_date).days
            duration = f"{duration_days} days"
        else:
            duration = None

        return cls(
            id=airdrop.id,
            title=airdrop.title,
            image_url=airdrop.image_url,
            duration=duration,
            status=airdrop.status,
            task_progress=task_progress
        )

    class Config:
        from_attributes = True