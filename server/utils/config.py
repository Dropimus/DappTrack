# config.py
import os
from pathlib import Path
from functools import lru_cache

def read_secret(name: str) -> str:
    """
    Look up the environment variable <NAME>_FILE, read its contents, and strip whitespace.
    Raises RuntimeError if the env‐var is missing or points to a non‐existent file.
    """
    file_env = f"{name}_FILE"
    secret_path = os.getenv(file_env)

    # Debug print so you can see exactly what paths were (or were not) passed in:
    print(f"DEBUG: Looking for {file_env} → {secret_path!r}")

    if not secret_path or not Path(secret_path).exists():
        raise RuntimeError(f"Missing or invalid secret file for: {name} (expected env var {file_env})")

    return Path(secret_path).read_text().strip()


class Settings:
    def __init__(self):
        # Each of these will raise a RuntimeError if the corresponding <VAR>_FILE is not set
        # or the file does not exist. The pprint‐style debug above will show you which one fails.
        self.pguser: str             = read_secret("POSTGRES_USER")
        self.password: str           = read_secret("POSTGRES_PASSWORD")
        self.host: str               = read_secret("PGHOST")
        self.port: int               = int(read_secret("PGPORT"))
        self.db: str                 = read_secret("POSTGRES_DB")
        self.secret_key: str         = read_secret("SECRET_KEY")
        self.key: str                = read_secret("ENCRYPTION_KEY")
        self.fernet_key: str         = read_secret("FERNET_KEY")
        self.database_url: str       = read_secret("DATABASE_URL")
        self.celery_broker_url: str  = read_secret("CELERY_BROKER_URL")
        self.celery_result_backend: str = read_secret("CELERY_RESULT_BACKEND")

        # Static config values (never read from secrets)
        self.algorithm: str                       = "HS256"
        self.access_token_expires_minutes: int    = 30
        self.refresh_token_expires_days: int      = 7
        self.remember_me_refresh_token_expires_days: int = 30

# Only instantiate Settings once (so that repeated imports don’t re-read files)
@lru_cache()
def get_settings() -> Settings:
    return Settings()
