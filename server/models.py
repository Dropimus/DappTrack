from sqlalchemy import Column, Integer, String, text,Float, ForeignKey, DateTime,func, Boolean, Table, JSON, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from datetime import datetime



Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_admin = Column(Boolean, default=False)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True)
    full_name = Column(String(100), nullable=True) 
    password_hash = Column(String(128), nullable=False)
    level = Column(Integer, default=1, nullable=True)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    referral_code = Column(String(10), nullable=False, unique=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    dapp_points = Column(Float, default=0, nullable=True)
    streak_days = Column(Integer, default=0, nullable=True)
    last_streak_date = Column(DateTime, default=datetime.utcnow)
    settings = Column(MutableDict.as_mutable(JSONB), default=dict, nullable=False)

    # Relationships
    # referrals = relationship(
    #     "User", 
    #     backref="referrer", 
    #     primaryjoin="User.referral_code == foreign(User.referred_by)",
    #     remote_side=[referral_code]
    #     )
    referrer = relationship("User", remote_side=[id], backref="referrals", foreign_keys=[referred_by])
    tracked_airdrops = relationship('AirdropTracking', back_populates='user')
    ratings = relationship('AirdropRating', back_populates='user')
    timers = relationship("Timer", back_populates="user")
    transactions = relationship("PointsTransaction", back_populates="user", cascade="all, delete-orphan")
    

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    def has_signup_bonus(self):
        """Check if the user has already been awarded signup points"""
        return self.dapp_points >= 10



class Airdrop(Base):
    __tablename__ = 'airdrops'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_url = Column(String(250), nullable=False)
    name = Column(String(100), nullable=False)
    chain = Column(String(20))
    status = Column(String, default='active')
    cost_to_complete = Column(Integer, default=0,nullable=True)
    device_type = Column(String, default='desktop & mobile')
    description = Column(String, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow,nullable=False)
    category = Column(String(50), nullable=True)
    rating_value = Column(Float, default=0, nullable=True)  
    project_socials = Column(JSON, nullable=True)
    funding = Column(Float, nullable=True)
    completion_percent = Column(Integer, default=0.0, nullable=False)
    expected_tge_date = Column(DateTime, nullable=True)
    airdrop_start_date = Column(DateTime, nullable=True)
    airdrop_end_date = Column(DateTime, nullable=True)
    is_tracked = Column(Boolean, default=False)
    expected_token_ticker = Column(String, nullable=True)  # Token users will receive
    external_airdrop_url = Column(String, nullable=True)  # actual airdrop website or link to app
   
     

    # Relationships
    steps = relationship('AirdropStep', back_populates='airdrop', cascade='all, delete-orphan')
    trackers = relationship('AirdropTracking', back_populates='airdrop')
    timers = relationship('Timer', back_populates='airdrop')
    ratings = relationship('AirdropRating', back_populates='airdrop') 

    def __repr__(self):
        return f"<Airdrop(id={self.id}, name={self.name}, status={self.status}, chain={self.chain},category={self.category})>"


class AirdropStep(Base):
    __tablename__ = 'airdrop_steps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    airdrop_id = Column(Integer, ForeignKey('airdrops.id'), nullable=False)
    description = Column(String, nullable=False)
    step_order = Column(Integer, nullable=False)
    screenshot_url = Column(String(250), nullable=True)  

    # Relationship back to Airdrop
    airdrop = relationship('Airdrop', back_populates='steps')

    def __repr__(self):
        return f"<AirdropStep(id={self.id}, description={self.description})>"


class AirdropRating(Base):
    __tablename__ = 'airdrop_ratings'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    airdrop_id = Column(Integer, ForeignKey('airdrops.id'), primary_key=True)
    rating_value = Column(Float, nullable=False)

    user = relationship('User', back_populates='ratings')
    airdrop = relationship('Airdrop', back_populates='ratings')

    def __repr__(self):
        return f"<AirdropRating(user_id={self.user_id}, airdrop_id={self.airdrop_id}, rating_value={self.rating_value})>"



class AirdropTracking(Base):
    __tablename__ = 'airdrop_tracking'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    airdrop_id = Column(Integer, ForeignKey('airdrops.id'), primary_key=True)
    completed_steps = Column(Integer, default=0) # how many steps the user completes
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='tracked_airdrops')
    airdrop = relationship('Airdrop', back_populates='trackers')

    def __repr__(self):
        return f"<AirdropTracking(user_id={self.user_id}, airdrop_id={self.airdrop_id})>"


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)           
    amount = Column(Float, nullable=False)          
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(String, nullable=True)

    user = relationship("User", back_populates="transactions")





class UserNFTReward(Base):
    __tablename__ = 'user_nft_rewards'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    nft_id = Column(Integer, nullable=False)
    tier = Column(String, nullable=False)
    awarded_at = Column(DateTime(timezone=True), default=func.now())

class Timer(Base):
    __tablename__ = "timers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'),nullable=False)  
    airdrop_id = Column(Integer, ForeignKey("airdrops.id"), nullable=False)  
    reminder_interval = Column(Integer, nullable=False)  # Interval in seconds
    next_reminder_time = Column(DateTime, nullable=False)  
    is_active = Column(Boolean, default=True)  # To track if the timer is active

    # Relationships
    airdrop = relationship("Airdrop", back_populates="timers")
    user = relationship("User", back_populates="timers")



# def create_all_tables(engine):
#     Base.metadata.create_all(engine)


# To run migrations using alembic
# alembic revision --autogenerate -m "message"
# alembic upgrade head
 