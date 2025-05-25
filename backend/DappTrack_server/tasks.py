import celery_app
from celery_app import celery, loop
from datetime import datetime, timedelta
from sqlalchemy.future import select
from models import Timer

@celery.task(name='tasks.check_expired_timers')
def check_expired_timers():
    """
    Periodic Celery task to find expired timers and trigger reminders.
    Uses the dedicated event loop and pre-initialized sessionmaker.
    """
    print("Checking expired timers...")
    
    loop.run_until_complete(_check_expired_timers())

async def _check_expired_timers():
    #sessionmaker initialized in celery_app via worker_process_init
    AsyncSessionLocal = celery_app.CeleryAsyncSession
    if AsyncSessionLocal is None:
        raise RuntimeError("CeleryAsyncSession has not been initialized.")

    async with AsyncSessionLocal() as session:
        try:
            now = datetime.utcnow()
            stmt = select(Timer).where(
                Timer.is_active == True,
                Timer.next_reminder_time <= now
            )
            result = await session.execute(stmt)
            expired = result.scalars().all()

            for timer in expired:
                # TODO: replace print with actual notification logic
                print(f"Reminder for user {timer.user_id}, timer {timer.id}, for Airdrop {timer.airdrop_id}")
                if timer.reminder_interval:
                    # ensure it's an int/float, then wrap
                    secs = int(timer.reminder_interval)
                    timer.next_reminder_time += timedelta(seconds=secs)
                else:
                    timer.is_active = False
                session.add(timer)

            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Failed to check expired timers: {e}")

