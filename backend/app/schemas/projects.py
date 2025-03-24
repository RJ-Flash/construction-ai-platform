from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .users import User

# Shared properties
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    status: str = "active"

# Properties to receive via API on creation
class ProjectCreate(ProjectBase):
    pass

# Properties to receive via API on update
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

# Properties shared by models stored in DB
class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Properties to return via API
class Project(ProjectInDBBase):
    owner: Optional[User] = None

# Properties to return via API for list endpoint
class ProjectList(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Properties for project statistics
class ProjectStats(BaseModel):
    total_documents: int
    analyzed_documents: int
    total_elements: int
    quotes_count: dict
    total_value: float

    class Config:
        orm_mode = True

# Project with detailed stats and counts
class ProjectDetail(Project):
    document_count: int = 0
    element_count: int = 0
    quote_count: int = 0