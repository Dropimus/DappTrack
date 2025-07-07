from pydantic import BaseModel, HttpUrl, constr, Field
from typing import Dict
from datetime import datetime

class AirdropSubmission(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    chain: constr(strip_whitespace=True, min_length=1)
    status: constr(strip_whitespace=True, min_length=1)
    device: constr(strip_whitespace=True, min_length=1)
    funding: float
    cost_to_complete: float
    description: constr(strip_whitespace=True)
    category: constr(strip_whitespace=True, min_length=1)
    external_airdrop_url: HttpUrl
    expected_token_ticker: constr(strip_whitespace=True, min_length=1)
    airdrop_start_date: datetime
    airdrop_end_date: datetime
    project_socials: Dict[str, HttpUrl]