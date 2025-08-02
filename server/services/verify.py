import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from typing import List
from models.models import User, SubmissionVote, Submission
from workers.tasks import verify_submission_task

MIN_HUNTERS = 3
MIN_HONOR_POINTS = 150

async def assign_hunters_to_submission(submission: Submission, db: AsyncSession) -> List[User]:
    # Get eligible hunters
    result = await db.execute(
        select(User).where(
            User.honor_points >= MIN_HONOR_POINTS,
            User.id != submission.submitted_by
        )
    )
    hunters = result.scalars().all()

    if len(hunters) < MIN_HUNTERS:
        raise HTTPException(status_code=400, detail="Not enough eligible hunters")

    selected_hunters = random.sample(hunters, MIN_HUNTERS)

    # Create placeholder votes
    for hunter in selected_hunters:
        vote = SubmissionVote(submission_id=submission.id, hunter_id=hunter.id)
        db.add(vote)

    await db.commit()

    # Trigger async verification when enough votes come in
    verify_submission_task.delay(submission.id)

    return selected_hunters
