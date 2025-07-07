from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Annotated

from createDB import get_session
from models.models import Submission, SubmissionVote
from models.schemas import (
    UserScheme,
    SimpleAirdropSubmissionCreate,
    AdvancedAirdropSubmissionCreate,
    SubmissionRead,
    VoteCreate,
    ALLOWED_CATEGORIES
)
from utils.utils import get_current_active_user
from routers.verification import verify_submission

router = APIRouter(prefix="/submissions", tags=["submissions"])


async def queue_verification_task(submission_id: int, db: AsyncSession):
    try:
        await verify_submission(submission_id, db)
    except Exception as e:
        print(f"[QUEUE] Verification failed for submission {submission_id}: {e}")



@router.post("/simple", response_model=SubmissionRead)
async def create_simple_submission(
    data: SimpleAirdropSubmissionCreate, 
    background_tasks: BackgroundTasks,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session)
):
    submission = Submission(
        title=data.title,
        submitted_by=current_user.id,
        description=data.description,
        chain=data.chain,
        website=str(data.website),
        token_symbol=data.token_symbol,
        social_links=",".join([str(link) for link in data.social_links]),
        category=data.category,
        device_type=data.device_type,
        status="pending",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    background_tasks.add_task(queue_verification_task, new_submission.id, db)
    return submission


@router.post("/advanced", response_model=SubmissionRead)
async def create_advanced_submission(
    data: AdvancedAirdropSubmissionCreate, 
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],

    db: AsyncSession = Depends(get_session)
):
    submission = Submission(
        title=data.title,
        submitted_by=current_user.id,
        description=data.description,
        chain=data.chain,
        website=str(data.website),
        token_symbol=data.token_symbol,
        social_links=",".join([str(link) for link in data.social_links]),
        category=data.category,
        device_type=data.device_type,
        snapshot_date=data.snapshot_date,
        max_reward=data.max_reward,
        eligibility_summary=data.eligibility_summary,
        eligibility_criteria=data.eligibility_criteria.json() if data.eligibility_criteria else None,
        steps=data.steps.json() if data.steps else None,
        status="pending",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    # submission is saved, then verified automatically
    try:
        await verify_submission(submission.id, db)
    except Exception as e:
        # Log or handle verification errors, but submission stays in "pending" if verification fails
        print(f"Verification error: {e}")

    return submission



@router.post("/{submission_id}/vote")
async def submit_vote(
    submission_id: int,
    vote_in: VoteCreate,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
):
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status != "pending":
        raise HTTPException(status_code=400, detail="Submission already processed")

    if current_user.honor_points < 150:
        raise HTTPException(status_code=403, detail="User not eligible to vote")

    existing_vote = await db.execute(
        select(SubmissionVote).where(
            SubmissionVote.submission_id == submission_id,
            SubmissionVote.user_id == current_user.id
        )
    )

    if existing_vote.first():
        raise HTTPException(status_code=400, detail="You have already voted on this submission")

    vote = SubmissionVote(
        submission_id=submission_id,
        user_id=current_user.id,
        vote=vote_in.vote,
    )
    db.add(vote)
    await db.commit()

    return {"message": "Vote recorded."}

@router.post("/{submission_id}/verify", response_model=SubmissionRead)
async def trigger_verification(submission_id: int, db: AsyncSession = Depends(get_session)):
    verified_submission = await verify_submission(submission_id, db)
    return verified_submission
