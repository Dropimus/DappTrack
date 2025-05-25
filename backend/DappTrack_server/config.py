from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    pguser: str = Field(..., alias='POSTGRES_USER')
    password: str = Field(..., alias='POSTGRES_PASSWORD')
    host: str = Field(..., alias='PGHOST')
    port: str = Field(..., alias='PGPORT')
    db: str = Field(..., alias='POSTGRES_DB')
    secret_key: str = Field(..., alias='SECRET_KEY')
    key: str = Field(..., alias='ENCRYPTION_KEY')
    fernet_key: str = Field(..., alias='FERNET_KEY')
    database_url: str = Field(..., alias='DATABASE_URL')
    celery_broker_url: str = Field(..., alias='CELERY_BROKER_URL')
    celery_result_backend: str = Field(..., alias='CELERY_RESULT_BACKEND')
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 7
    remember_me_refresh_token_expires_days: int = 30

    class Config:
        env_file = ".env"
        extra = "forbid"
        validate_by_name = True

settings = Settings()