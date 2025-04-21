import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models import Base

user = os.getenv('PGUSER')
password = os.getenv('PGPASSWORD') 
host = os.getenv('PGHOST')
port = os.getenv('PGPORT')
db = os.getenv('PGDB')


ssl = "?ssl=require"

# Async function to create the async engine
async def get_engine(user, passwd, host, port, db):
    # Connect to the default postgres database 
    default_url = f"postgresql+asyncpg://{user}:{passwd}@{host}:{port}/postgres{ssl}"
    default_engine = create_async_engine(default_url, echo=True)

    async with default_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"), {"db_name": db}
        )
        exists = result.scalar()

        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{db}"'))
            await conn.commit()

    await default_engine.dispose()

    # create the engine for the actual database
    db_url = f"postgresql+asyncpg://{user}:{passwd}@{host}:{port}/{db}{ssl}"
    engine = create_async_engine(db_url, echo=True)
    return engine

# Create a sessionmaker for AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}{ssl}",
        echo=True
    ),
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Commit after yielding, if needed
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()  # Rollback in case of error
            print(f"Database error: {e}")
            raise  # Re-raise the exception to propagate it
        finally:
            await session.close() 

# Create all tables asynchronously
async def init_db(engine):
    try:
        async with engine.begin() as conn:
            print('Database about to be created')
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error during DB initialization: {e}")
    finally:
        await engine.dispose()


# Runs the initialization if this script is executed directly
if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().get_event_loop()
    engine = loop.run_until_complete(get_engine(user, password, host, port, db))
    loop.run_until_complete(init_db(engine))











############### Custom alembic script 


# import asyncio
# from logging.config import fileConfig
# from sqlalchemy.ext.asyncio import async_engine_from_config
# from sqlalchemy import pool
# from alembic import context

# from models import Base  

# # Alembic Config
# config = context.config
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
# print(db_url)
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
