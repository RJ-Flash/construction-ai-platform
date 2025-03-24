from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Shared properties
class ElementBase(BaseModel):
    type: str
    materials: Optional[str] = None
    dimensions: Optional[str] = None
    quantity: Optional[float] = 1.0
    estimated_price: Optional[float] = None
    notes: Optional[str] = None
    document_id: Optional[int] = None
    project_id: Optional[int] = None

# Properties to receive via API on creation
class ElementCreate(ElementBase):
    pass

# Properties to receive via API on update
class ElementUpdate(BaseModel):
    type: Optional[str] = None
    materials: Optional[str] = None
    dimensions: Optional[str] = None
    quantity: Optional[float] = None
    estimated_price: Optional[float] = None
    notes: Optional[str] = None
    document_id: Optional[int] = None
    project_id: Optional[int] = None

# Properties shared by models stored in DB
class ElementInDBBase(ElementBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Properties to return via API
class Element(ElementInDBBase):
    pass

# Element with document name
class ElementWithDocument(Element):
    document_name: Optional[str] = None

# Element with related elements
class ElementDetail(Element):
    related_elements: Optional[List['ElementBase']] = []

# Element filter
class ElementFilter(BaseModel):
    type: Optional[str] = None
    materials: Optional[str] = None
    project_id: Optional[int] = None
    document_id: Optional[int] = None
    
# Element stats
class ElementStats(BaseModel):
    total_count: int
    by_type: dict
    by_material: dict
    by_document: dict
    estimated_total_value: Optional[float] = None