from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.db.models.project import ProjectStatus

class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

    @validator("status")
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in ProjectStatus]:
            raise ValueError(f"Invalid status. Must be one of: {', '.join([status.value for status in ProjectStatus])}")
        return v

class ProjectCreate(ProjectBase):
    name: str

class ProjectUpdate(ProjectBase):
    total_estimate: Optional[float] = None

class ProjectInDBBase(ProjectBase):
    id: int
    user_id: int
    total_estimate: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProjectResponse(ProjectInDBBase):
    document_count: Optional[int] = None
    estimation_count: Optional[int] = None
