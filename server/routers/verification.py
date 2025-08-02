from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import random
from createDB import get_session
from models.models import Submission, User
from services.verify import assign_hunters_to_submission

router = APIRouter(prefix="/verification", tags=["verification"])

@router.post("/start/{submission_id}")
async def start_verification(submission_id: int, db: AsyncSession = Depends(get_session)):
    # Fetch submission
    stmt = select(Submission).where(Submission.id == submission_id)
    result = await db.execute(stmt)
    submission = result.scalars().first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.status != "pending":
        raise HTTPException(status_code=400, detail="Submission is not pending")

    selected_hunters = await assign_hunters_to_submission(submission, db)
    return {
        "message": f"Verification started for submission {submission_id}",
        "hunters_assigned": [hunter.username for hunter in selected_hunters]
    }
