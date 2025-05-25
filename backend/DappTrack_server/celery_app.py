from celery import Celery
from celery.signals import worker_process_init
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings

# one event loop for all Celery async work
loop = asyncio.new_event_loop()

DATABASE_URL = settings.database_url
engine = None
CeleryAsyncSession = None

@worker_process_init.connect
def init_db(**kwargs):
    """
    Initialize one AsyncEngine and async_sessionmaker per worker process,
    binding them to the dedicated event loop.
    """
    asyncio.set_event_loop(loop)

    global engine, CeleryAsyncSession
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
    )
    CeleryAsyncSession = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    print(f"[init_db] Engine & sessionmaker initialized on loop id={id(loop)}")


celery = Celery(
    "dapptrack_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks"],
)

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'check-expired-timers-every-minute': {
            'task': 'tasks.check_expired_timers',
            'schedule': 10.0,
        },
    }
)


# redis-server
# celery -A celery_app worker --loglevel=info
# celery -A celery_app beat   --loglevel=info
