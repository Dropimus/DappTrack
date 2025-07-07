from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Airdrop(Base):
    __tablename__ = "airdrops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    chain = Column(String(100), nullable=False)
    status = Column(String(100), nullable=False)
    device_type = Column(String(100), nullable=False)
    funding = Column(String(100), nullable=False)
    cost_to_complete = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    external_airdrop_url = Column(String(255), unique=True, nullable=False)
    expected_token_ticker = Column(String(50), nullable=False)
    airdrop_start_date = Column(DateTime, nullable=False)
    airdrop_end_date = Column(DateTime, nullable=False)
    project_socials = Column(JSON)
    image_url = Column(String(255))