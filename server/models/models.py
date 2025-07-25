from sqlalchemy import (
    Column, Integer, String, Float, 
    ForeignKey, DateTime, Boolean, func, 
    JSON, UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_admin = Column(Boolean, default=False)
    username = Column(String(50), nullable=False, unique=True)
    title = Column(String, default="Chosen Seeker")
    email = Column(String(120), nullable=False, unique=True)
    full_name = Column(String(100), nullable=True)
    password_hash = Column(String(128), nullable=False)
    level = Column(Integer, default=1, nullable=True)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    referral_code = Column(String(10), nullable=False, unique=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String, default="user", nullable=False)
    honor_points = Column(Float, default=0, nullable=True)
    streak_days = Column(Integer, default=0, nullable=True)
    last_streak_date = Column(DateTime, default=datetime.utcnow)
    settings = Column(MutableDict.as_mutable(JSONB), default=dict, nullable=False)

    # relationships
    fcm_tokens = relationship("FCMToken", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="submitter")
    referrer = relationship(
        "User", remote_side=[id], backref="referrals", foreign_keys=[referred_by]
    )
    tracked_airdrops = relationship("AirdropTracking", back_populates="user")
    timers = relationship("Timer", back_populates="user")
    transactions = relationship("PointsTransaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class FCMToken(Base):
    __tablename__ = "fcm_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    token = Column(String, nullable=False)
    created_at = Column(DateTime)

    user = relationship("User", back_populates="fcm_tokens")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(250), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    website = Column(String, nullable=False)
    token_symbol = Column(String, nullable=False)
    cost_to_complete = Column(Integer, default=0,nullable=True)
    device_type = Column(String, default='desktop & mobile')
    category = Column(String(50), nullable=True)
    project_socials = Column(JSON, nullable=True)

    snapshot_date = Column(DateTime, nullable=True)
    max_reward = Column(Float, nullable=True)
    eligibility_summary = Column(String, nullable=True)
    eligibility_criteria = Column(String, nullable=True)
    steps_text = Column(String, nullable=True)
    intel_note = Column(String, nullable=True)
    funding = Column(Float, nullable=True)
    referral_link = Column(String, nullable=True)

    status = Column(String, default="pending", nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    accuracy_multiplier = Column(Float, default=1.0, nullable=False)
    rating_value = Column(Float, default=0.0, nullable=False)
    airdrop_start_date = Column(DateTime, nullable=True)
    airdrop_end_date = Column(DateTime, nullable=True)

    # relationships
    submitter = relationship("User", back_populates="submissions")
    steps = relationship("AirdropStep", back_populates="submission", cascade="all, delete-orphan")
    trackers = relationship("AirdropTracking", back_populates="submission", cascade="all, delete-orphan")
    timers = relationship("Timer", back_populates="submission", cascade="all, delete-orphan")
    votes = relationship("SubmissionVote", back_populates="submission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Submission(id={self.id}, title={self.title}, status={self.status})>"


class SubmissionVote(Base):
    __tablename__ = "submission_votes"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote = Column(String, nullable=False)

    submission = relationship("Submission", back_populates="votes")


class AirdropStep(Base):
    __tablename__ = "airdrop_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    description = Column(String, nullable=False)
    step_order = Column(Integer, nullable=False)
    screenshot_url = Column(String(250), nullable=True)

    submission = relationship("Submission", back_populates="steps")

    def __repr__(self):
        return f"<AirdropStep(id={self.id}, order={self.step_order})>"


class AirdropTracking(Base):
    __tablename__ = "airdrop_tracking"

    __table_args__ = (
        UniqueConstraint("user_id", "submission_id", name="uix_user_submission"),
    )
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), primary_key=True)
    completed_steps = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tracked_airdrops")
    submission = relationship("Submission", back_populates="trackers")

    def __repr__(self):
        return f"<AirdropTracking(user_id={self.user_id}, submission_id={self.submission_id})>"


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(String, nullable=True)
    reference_id = Column(String, unique=True, nullable=True)

    user = relationship("User", back_populates="transactions")


class UserNFTReward(Base):
    __tablename__ = "user_nft_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nft_id = Column(Integer, nullable=False)
    tier = Column(String, nullable=False)
    awarded_at = Column(DateTime(timezone=True), default=func.now())


class Timer(Base):
    __tablename__ = "timers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    reminder_interval = Column(Integer, nullable=False)
    next_reminder_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="timers")
    submission = relationship("Submission", back_populates="timers")






# To run migrations using alembic
# alembic revision --autogenerate -m "message"
# alembic upgrade head
 