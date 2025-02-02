from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Usage(BaseModel):
    machine_id: str
    count: int = 0
    last_used: Optional[datetime] = None
    created_at: Optional[datetime] = None
    api_key: Optional[str] = None
    plan: Optional[str] = None
