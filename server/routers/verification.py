from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from createDB import get_session
from models.models import Submission, User
from models.schemas import SubmissionRead
from utils.honor_calculation import compute_total_honor

router = APIRouter(prefix="/verification", tags=["verification"])


async def send_to_hunter_pool(submission: Submission, db: AsyncSession) -> List[str]:
    # Select 3 random Centurion+ users (HONOR >= 150) who are not the submitter
    result = await db.execute(
        select(User).where(
            User.honor_points >= 150,
            User.id != submission.submitted_by
        )
    )
    hunters = result.scalars().all()

    if len(hunters) < 3:
        raise HTTPException(status_code=400, detail="Not enough eligible hunters available for verification.")

    selected_hunters = random.sample(hunters, 3)

    # TODO: Replace with actual vote collection system
    # For now, mocked votes: random "approve" or "reject"
    votes = [random.choice(["approve", "reject"]) for _ in selected_hunters]

    return votes



async def verify_submission(submission_id: int, db: AsyncSession):
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status != "pending":
        raise HTTPException(status_code=400, detail="Submission already processed")

    # Placeholder for AI analysis (Coming soon)
    ai_confidence = None  # TODO: integrate AI model prediction here

    # Proceed to human verification regardless of AI output
    hunter_votes = await send_to_hunter_pool(submission)

    # Determine verdict
    if hunter_votes.count("reject") >= 2:
        # TODO: Future logic → classify as "scam" or "false" with extra input or AI
        verdict = "scam"  # Using "scam" by default for now; refine later
        submission.status = "rejected"
    elif hunter_votes.count("approve") >= 2:
        verdict = "legit"
        submission.status = "verified"
    else:
        submission.status = "rejected"

    # Award HONOR to submitting user (if applicable)
    submitter = await db.get(User, submission.submitted_by)
    if not submitter:
        raise HTTPException(status_code=404, detail="Submitter not found")

    honor_change = compute_total_honor(
        verdict=verdict,
        accuracy_multiplier=submitter.accuracy_multiplier or 1.0,
        streak_count=submitter.verification_streak or 0,
        current_honor=submitter.honor_points or 0,
    )

    await record_points_transaction(
        user_id=submitter.id,
        txn_type="submission_verification",
        amount=honor_change,
        description=f"Submission verified as {verdict}",
        reference_id=f"submission_verification:{submission_id}",  # <-- here
        db=db,
    )

    await db.commit()
    await db.refresh(submission)
    return submission


@router.post("/{submission_id}", response_model=SubmissionRead)
async def trigger_verification(submission_id: int, db: AsyncSession = Depends(get_session)):
    verified_submission = await verify_submission(submission_id, db)
    return verified_submission
