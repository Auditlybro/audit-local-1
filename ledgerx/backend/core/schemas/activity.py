from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union

class ActivityLogResponse(BaseModel):
    id: UUID
    company_id: Optional[UUID]
    user_id: Optional[UUID]
    user_name: Optional[str] = None
    action: str
    description: str
    metadata_json: Optional[Union[Dict[str, Any], list]]
    created_at: datetime

    class Config:
        from_attributes = True

class ActivityLogList(BaseModel):
    logs: List[ActivityLogResponse]
    total: int
    page: int
    page_size: int
