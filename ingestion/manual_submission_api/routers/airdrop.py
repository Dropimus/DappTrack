from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime

from db import get_session
from models import Airdrop, Base
from schemas import AirdropSubmission
from utils.image_upload import save_airdrop_image

router = APIRouter()

@router.post("/submit_airdrop")
async def submit_airdrop(
    image: UploadFile = File(...),
    form_data: str = Form(...),
    db: AsyncSession = Depends(get_session)
):
    # Validate input
    try:
        data = json.loads(form_data)
        payload = AirdropSubmission(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in form_data")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Check existing
    q = select(Airdrop).filter_by(external_airdrop_url=payload.external_airdrop_url)
    res = await db.execute(q)
    existing = res.scalars().first()

    try:
        if existing:
            filename = await save_airdrop_image(existing.id, image)
            existing.status = payload.status
            existing.funding = str(payload.funding)
            existing.description = payload.description
            existing.category = payload.category
            existing.project_socials = payload.project_socials
            existing.airdrop_start_date = payload.airdrop_start_date
            existing.airdrop_end_date = payload.airdrop_end_date
            existing.image_url = f"/static/airdrop_image/{filename}"
            await db.commit()
            return {"message": "Airdrop updated", "id": existing.id}

    
        new_airdrop = Airdrop(
            name=payload.name.title(),
            chain=payload.chain.lower(),
            status=payload.status.lower(),
            device_type=payload.device.lower(),
            funding=str(payload.funding),
            cost_to_complete=str(payload.cost_to_complete),
            description=payload.description,
            category=payload.category,
            external_airdrop_url=payload.external_airdrop_url,
            expected_token_ticker=payload.expected_token_ticker.upper(),
            airdrop_start_date=payload.airdrop_start_date,
            airdrop_end_date=payload.airdrop_end_date,
            project_socials=payload.project_socials,
            image_url=""
        )
        db.add(new_airdrop)
        await db.commit()
        await db.refresh(new_airdrop)

        filename = await save_airdrop_image(new_airdrop.id, image)
        new_airdrop.image_url = f"/static/airdrop_image/{filename}"
        await db.commit()

        return {"message": "Airdrop created", "id": new_airdrop.id}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed processing: {e}")