from celery import Celery
from datetime import datetime, timedelta
from createDB import get_session
from models import Timer
from notification import send_notification

celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
def schedule_reminder(timer_id):
    db = SessionLocal()
    timer = db.query(Timer).filter(Timer.id == timer_id).first()
    
    if timer:
        # Send a notification
        send_notification(timer.user_id, timer.airdrop_id)
        
        # Update the timer for the next reminder
        timer.next_reminder_time = datetime.utcnow() + timedelta(seconds=timer.interval_seconds)
        db.commit()
        
        # Reschedule the task
        schedule_reminder.apply_async(
            args=[timer.id],
            countdown=timer.interval_seconds
        )
