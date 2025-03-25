from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    secret_key: str = os.getenv('SECRET_KEY')
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 7  
    remember_me_refresh_token_expires_days: int = 30  

    class Config:
        env_file = ".env"

settings = Settings()


# to get a string like this run:
# openssl rand -hex 32