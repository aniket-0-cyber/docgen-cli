from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Usage(BaseModel):
    request_type: str
    machine_id: Optional[str] = None
    api_key: Optional[str] = None
    plan: Optional[str] = None
    timestamp: Optional[datetime] = None 
    count: Optional[int] = None