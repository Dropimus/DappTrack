import os
import asyncio
import ssl
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from asyncpg import ConnectionDoesNotExistError
from models.models import Base
from utils.config import get_settings

settings = get_settings()

PG_USER = settings.pguser
PG_PASS = settings.password
PG_HOST = settings.host     
PG_PORT = settings.port
PG_DB   = settings.db

# Toggle SSL via env (set SSL_MODE=require in production)
USE_SSL = os.getenv("SSL_MODE", "").lower() in ("require", "true", "1")

# SSL CONTEXT
def build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    # In prod you'd load CA certs:
    # ctx.verify_mode = ssl.CERT_REQUIRED
    # ctx.load_verify_locations(cafile="/path/to/ca.pem")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

SSL_CTX = build_ssl_context() if USE_SSL else None

# URL / ENGINE HELPERS 
def build_url(database: str) -> str:
    return f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{database}"

def make_engine(database: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(
        build_url(database),
        echo=echo,
        connect_args={"ssl": SSL_CTX} if SSL_CTX else {},
    )

ENGINE: AsyncEngine = make_engine(PG_DB, echo=True)

async def ensure_db():
    """Connect to 'postgres' and CREATE DATABASE if missing."""
    default = make_engine("postgres", echo=False)
    try:
        async with default.begin() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :db"),
                {"db": PG_DB}
            )
            if not exists:
                print(f"[DB Init] Creating database '{PG_DB}'...")
                await conn.execute(text(f'CREATE DATABASE "{PG_DB}"'))
                print(f"[DB Init] Database created.")
    finally:
        await default.dispose()

async def init_tables():
    """Create all tables from your SQLAlchemy models."""
    async with ENGINE.begin() as conn:
        print("[DB Init] Creating tables…")
        await conn.run_sync(Base.metadata.create_all)
        print("[DB Init] Tables ready.")

async def bootstrap_db(retries: int = 5, delay: float = 2.0):
    """Run ensure_db + init_tables with retry on early startup failures."""
    for attempt in range(1, retries + 1):
        try:
            await ensure_db()
            await init_tables()
            print("[DB Init] Bootstrap complete.")
            return
        except (ConnectionRefusedError, ConnectionDoesNotExistError) as e:
            print(f"[DB Init] Attempt {attempt}/{retries} failed: {e!r}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                raise

AsyncSessionLocal = sessionmaker(
    bind=ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session():
    """FastAPI dependency: yields a session, commits or rollbacks on exit."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

if __name__ == "__main__":
    # e.g. `SSL_MODE=require python create_db.py`
    asyncio.run(bootstrap_db())



















############### Custom alembic script 



# import os
# import asyncio
# from logging.config import fileConfig

# from alembic import context
# from sqlalchemy.ext.asyncio import async_engine_from_config
# from sqlalchemy import pool

# from models import Base  

# # Alembic Config
# config = context.config

# db_url = os.getenv("DB_URL")
# if not db_url:
#     raise RuntimeError("Environment variable DB_URL is not set")

# config.set_main_option("sqlalchemy.url", db_url)



# # set up py logging
# fileConfig(config.config_file_name)

# target_metadata = Base.metadata


# def run_migrations_offline():
#     """Run migrations in 'offline' mode."""
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# async def run_migrations_online():
#     """Run migrations in 'online' mode."""
#     connectable = async_engine_from_config(
#         config.get_section(config.config_ini_section),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     async with connectable.connect() as connection:
#         def do_run_migrations(sync_connection):
#             context.configure(
#                 connection=sync_connection,
#                 target_metadata=target_metadata,
#                 compare_type=True,
#             )
#             with context.begin_transaction():
#                 context.run_migrations()

#         await connection.run_sync(do_run_migrations)

#     await connectable.dispose()


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     asyncio.run(run_migrations_online())
