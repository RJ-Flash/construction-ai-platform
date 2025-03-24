"""
Schema definitions for projects.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    location: Optional[str] = Field(None, description="Project location")
    client_name: Optional[str] = Field(None, description="Client name")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    status: Optional[str] = Field("planning", description="Project status")


class ProjectCreate(ProjectBase):
    """Schema for project creation."""
    class Config:
        schema_extra = {
            "example": {
                "name": "Commercial Building Renovation",
                "description": "Renovation of a 3-story commercial building",
                "location": "123 Main St, New York, NY",
                "client_name": "ABC Corporation",
                "start_date": "2025-04-15T00:00:00",
                "end_date": "2025-10-30T00:00:00",
                "status": "planning"
            }
        }


class ProjectUpdate(BaseModel):
    """Schema for project updates."""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "in-progress",
                "end_date": "2025-11-15T00:00:00"
            }
        }


class ProjectInDBBase(ProjectBase):
    """Project schema with DB fields."""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Project(ProjectInDBBase):
    """Project response schema."""
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Commercial Building Renovation",
                "description": "Renovation of a 3-story commercial building",
                "location": "123 Main St, New York, NY",
                "client_name": "ABC Corporation",
                "start_date": "2025-04-15T00:00:00",
                "end_date": "2025-10-30T00:00:00",
                "status": "planning",
                "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_at": "2025-03-24T12:34:56",
                "updated_at": "2025-03-24T12:34:56"
            }
        }
