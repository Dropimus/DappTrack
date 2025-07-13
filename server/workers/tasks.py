from workers import celery_app
from .celery_app import celery, loop
from datetime import datetime, timedelta
from sqlalchemy.future import select
from models.models import Timer
from redis.asyncio.lock import Lock
from utils.redis import redis_client
from utils.honor_calculation import compute_total_honor


@celery.task(name='tasks.check_expired_timers')
def check_expired_timers():
    """
    Periodic Celery task to find expired timers and trigger reminders.
    Uses a Redis lock to prevent overlapping executions.
    """
    loop.run_until_complete(_check_expired_timers_with_lock())


async def _check_expired_timers_with_lock():
    lock = Lock(redis_client, "lock:check_expired_timers", timeout=295)
    has_lock = await lock.acquire(blocking=False)

    if not has_lock:
        print("[check_expired_timers] Lock already held — skipping execution")
        return

    try:
        await _check_expired_timers()
    finally:
        await lock.release()


async def _check_expired_timers():
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
                print(f"Reminder for user {timer.user_id}, timer {timer.id}, for Airdrop {timer.submission_id}")
                if timer.reminder_interval:
                    secs = int(timer.reminder_interval)
                    timer.next_reminder_time += timedelta(seconds=secs)
                else:
                    timer.is_active = False
                session.add(timer)

            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Failed to check expired timers: {e}")



@celery.task(name='tasks.verify_submission')
def verify_submission_task(submission_id: int):
    print(f"[CELERY] Verifying submission {submission_id}")
    loop.run_until_complete(_verify_submission(submission_id))


async def _verify_submission(submission_id: int):
    AsyncSessionLocal = celery_app.CeleryAsyncSession
    if AsyncSessionLocal is None:
        raise RuntimeError("CeleryAsyncSession has not been initialized.")

    async with AsyncSessionLocal() as session:
        stmt = select(Submission).where(Submission.id == submission_id).with_for_update()
        result = await session.execute(stmt)
        submission = result.scalars().first()

        if not submission:
            print(f"Submission {submission_id} not found.")
            return

        if submission.status != "pending":
            print(f"Submission {submission_id} already processed.")
            return

        # Placeholder for AI confidence score
        ai_confidence = None  # TODO: integrate AI prediction later

        # Gather votes
        result = await session.execute(
            select(SubmissionVote.vote).where(SubmissionVote.submission_id == submission_id)
        )
        votes = [row[0] for row in result.all()]

        if len(votes) < 3:
            print(f"Submission {submission_id} does not have enough votes yet.")
            return

        # Verdict logic
        if votes.count("reject") >= 2:
            verdict = "scam"
            submission.status = "rejected"
        elif votes.count("approve") >= 2:
            verdict = "legit"
            submission.status = "verified"
        else:
            verdict = "rejected"
            submission.status = "rejected"

        # HONOR reward
        submitter = await session.get(User, submission.submitted_by)
        if submitter:
            honor_change = compute_total_honor(
                verdict=verdict,
                accuracy_multiplier=submitter.accuracy_multiplier or 1.0,
                streak_count=submitter.verification_streak or 0,
                current_honor=submitter.honor_points or 0,
            )

            honor_change = max(-submitter.honor_points, honor_change)  # Prevent overflow

            await record_points_transaction(
                user_id=submitter.id,
                txn_type="submission_verification",
                amount=honor_change,
                description=f"Submission [{submission.id}] verified as {verdict}",
                reference_id=f"submission_verification:{submission_id}",
                db=session
            )

        await session.commit()
        print(f"[SUCCESS] Submission {submission_id} verified. {honor_change} HONOR applied.")
