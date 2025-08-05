from pydantic import BaseModel, Field, EmailStr, constr, root_validator, HttpUrl
from typing import Optional, List, Dict, Any, Union, Annotated
from datetime import datetime, date
from enum import Enum
from utils.chains import CHAINS  


ALLOWED_CHAIN_SLUGS = [chain["slug"] for chain in CHAINS]



class AirdropStatus(str, Enum):
    PENDING = "pending"
    UPCOMING = "upcoming"
    ACTIVE = "active"
    ENDED = "ended"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    BOTH = "desktop & mobile"


class AirdropCategory(str, Enum):
    STANDARD = "standard"
    RETROACTIVE = "retroactive"
    SOCIALFI = "socialfi"
    INFOFI = "infofi"
    GAMEFI = "gamefi"
    MINING = "mining"
    TESTNET = "testnet"
    NFT = "nft"
    TRADING = "trading"
    PROTOCOL = "protocol"
    STAKING = "staking"
    GUILD = "guild"
    AI = "ai"

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



# ---------------- BASE SCHEMA ---------------- #

class AirdropBaseSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    chain: str = Field(..., description="Slug of the blockchain (e.g., ethereum, bnb, polygon)")
    status: AirdropStatus
    website: HttpUrl
    device_type: DeviceType
    funding: Optional[float] = None
    cost_to_complete: Optional[int] = None
    description: str = Field(..., min_length=10)
    category: AirdropCategory
    referral_link: str
    token_symbol: str = Field(..., min_length=1, max_length=10)
    airdrop_start_date: datetime
    airdrop_end_date: datetime
    project_socials: Dict[str, Any]

    @root_validator(pre=True)
    def validate_chain(cls, values):
        chain = values.get("chain")
        if chain not in ALLOWED_CHAIN_SLUGS:
            raise ValueError(f"Invalid chain: {chain}. Allowed values are: {', '.join(ALLOWED_CHAIN_SLUGS)}")
        return values


# ---------------- CREATE SCHEMA ---------------- #

class AirdropCreateSchema(AirdropBaseSchema):
    image_url: HttpUrl 


# ---------------- RESPONSE SCHEMA ---------------- #

class AirdropResponse(BaseModel):
    id: int
    image_url: str
    title: str
    chain: str
    status: str
    rating_value: Optional[float]
    website: str
    device_type: str
    funding: Optional[float]
    cost_to_complete: Optional[int]
    description: str
    category: str
    referral_link: str
    token_symbol: str
    airdrop_start_date: datetime
    airdrop_end_date: datetime
    project_socials: Dict[str, Any]
    # is_verified: bool
    # created_at: datetime

    class Config:
        from_attributes = True



class AirdropTrackRequest(BaseModel):
    submission_id: int

class TimerRequest(BaseModel):
    submission_id: int
    total_seconds: int


class TokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

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

class Instruction(BaseModel):
    text: str
    link: Optional[str] = None

class AirdropStepCreate(BaseModel):
    step_number: int
    title: str = Field(..., min_length=3)
    instructions: List[Instruction]
    image_url: Optional[str] = None  # Add this

class AirdropStepResponse(BaseModel):
    id: int
    step_number: int
    title: str
    instructions: List[Instruction]
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
