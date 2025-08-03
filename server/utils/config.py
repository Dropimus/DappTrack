import os
from functools import lru_cache
from dotenv import load_dotenv

# Detect local dev
is_local = os.getenv("ENV") != "docker"

# Always load .env, and optionally load .env.local if present and not in Docker
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(base_dir, ".env"))
if is_local:
    load_dotenv(os.path.join(base_dir, ".env.local"), override=True)

def get_env(name: str) -> str:
    """Fetch an env‑var or blow up if it’s missing/empty."""
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

class Settings:
    def __init__(self):
        # core Postgres
        self.pguser                = get_env("POSTGRES_USER")
        self.password              = get_env("POSTGRES_PASSWORD")
        self.host                  = get_env("POSTGRES_HOST")
        self.port                  = int(get_env("POSTGRES_PORT"))
        self.db                    = get_env("POSTGRES_DB")

        # app secrets & URLs
        self.secret_key            = get_env("SECRET_KEY")
        self.encryption_key        = get_env("ENCRYPTION_KEY")
        self.fernet_key            = get_env("FERNET_KEY")
        self.database_url          = get_env("DATABASE_URL")
        self.celery_broker_url     = get_env("CELERY_BROKER_URL")
        self.celery_result_backend = get_env("CELERY_RESULT_BACKEND")

        # static defaults
        self.algorithm                          = "HS256"
        self.access_token_expires_minutes       = 30
        self.access_token_expires_days          = 1
        self.refresh_token_expires_minutes      = 60 * 24 * 7
        self.refresh_token_expires_days         = 7
        self.remember_me_refresh_token_expires_days = 30

@lru_cache()
def get_settings() -> Settings:
    return Settings()
