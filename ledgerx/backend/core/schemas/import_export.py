"""Import/export schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ImportSessionResponse(BaseModel):
    id: UUID
    company_id: UUID
    source_type: str
    file_name: str | None
    status: str
    total_records: int
    imported_records: int
    error_records: int
    errors_json: dict | list | None
    created_at: datetime | None

    class Config:
        from_attributes = True


class ImportHistoryResponse(BaseModel):
    sessions: list[ImportSessionResponse]


class RollbackResponse(BaseModel):
    session_id: UUID
    rolled_back: bool
    message: str
