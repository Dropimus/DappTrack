from pydantic import BaseModel, Field, EmailStr, constr, validator, HttpUrl
from typing import Optional, List, Dict, Any, Union, Annotated
from datetime import datetime, date

ALLOWED_CATEGORIES = {
    'standard', 'retroactive', 'socialfi', 'infofi', 'gamefi', 'mining',
    'testnet', 'nft', 'trading', 'protocol', 'staking', 'guild', 'ai'
}
ALLOWED_DEVICE_TYPES = {"desktop", "mobile", "desktop & mobile"}

class SignupRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")]
    full_name: str
    email: EmailStr
    password: str
    referral_code: Optional[str] = None


class LoginRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")]
    password: str
    remember_me: Optional[bool] = False

class NotificationRequest(BaseModel):
    token: str
    title: str
    body: str


class FirebaseTokenRequest(BaseModel):
    id_token: str

class UpdatePasswordSchema(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class AirdropCreateSchema(BaseModel):
    title: str
    chain: str
    status: str
    website: HttpUrl
    device: str
    funding: Optional[str] = None
    cost_to_complete: Optional[str] = None
    description: str
    category: str
    referral_link: str
    token_symbol: str
    airdrop_start_date: datetime
    airdrop_end_date: datetime
    project_socials: Dict[str, Any]

class AirdropTrackRequest(BaseModel):
    submission_id: int

class TimerRequest(BaseModel):
    submission_id: int
    total_seconds: int


class EncryptTokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None

class RatingRequestSchema(BaseModel):
    submission_id: int
    rating: float

class UserScheme(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    honor_points: Optional[float]
    referral_code: Optional[str]
    referred_by: Optional[int]
    is_admin: Optional[bool]
    title: Optional[str] = None

    class Config:
        from_attributes = True

# --- Referred User (for referrals endpoint) ---
class ReferredUser(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True

# --- Tracked Airdrop (for tracked airdrops endpoint) ---
class TrackedAirdropSchema(BaseModel):
    id: int
    title: str
    image_url: Optional[str] = None
    status: Optional[str] = None
    task_progress: Optional[float] = None
    duration: Optional[str] = None

    @classmethod
    def from_orm_with_duration(cls, airdrop, task_progress: float):
        duration = None
        if hasattr(airdrop, "airdrop_start_date") and hasattr(airdrop, "airdrop_end_date"):
            if airdrop.airdrop_start_date and airdrop.airdrop_end_date:
                duration_days = (airdrop.airdrop_end_date - airdrop.airdrop_start_date).days
                duration = f"{duration_days} days"
        return cls(
            id=airdrop.id,
            title=airdrop.title,
            image_url=getattr(airdrop, "image_url", None),
            status=getattr(airdrop, "status", None),
            task_progress=task_progress,
            duration=duration
        )

    class Config:
        from_attributes = True

class SettingsSchema(BaseModel):
    theme: Optional[str] = "light"
    notifications: Optional[bool] = True
    language: Optional[str] = "en"

class UserSettingsResponse(BaseModel):
    user_id: int
    settings: Dict[str, Any]

# --- Generic API Response Models ---
class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class UserResponse(GenericResponse):
    data: Optional[UserScheme]

class UsersListResponse(GenericResponse):
    data: List[UserScheme]

class SettingsResponse(GenericResponse):
    data: Dict[str, Any]

class TrackedAirdropsResponse(GenericResponse):
    data: List[TrackedAirdropSchema]