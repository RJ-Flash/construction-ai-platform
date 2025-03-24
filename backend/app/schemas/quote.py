"""
Schema definitions for quotes.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class QuoteItemBase(BaseModel):
    """Base quote item schema."""
    description: str = Field(..., description="Item description")
    category: Optional[str] = Field(None, description="Item category")
    
    material_cost_min: Optional[float] = Field(0.0, description="Minimum material cost")
    material_cost_max: Optional[float] = Field(0.0, description="Maximum material cost")
    labor_cost_min: Optional[float] = Field(0.0, description="Minimum labor cost")
    labor_cost_max: Optional[float] = Field(0.0, description="Maximum labor cost")
    equipment_cost_min: Optional[float] = Field(0.0, description="Minimum equipment cost")
    equipment_cost_max: Optional[float] = Field(0.0, description="Maximum equipment cost")
    
    time_estimate_min: Optional[float] = Field(None, description="Minimum time estimate (hours)")
    time_estimate_max: Optional[float] = Field(None, description="Maximum time estimate (hours)")
    
    notes: Optional[str] = Field(None, description="Additional notes")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Additional specifications")


class QuoteItemCreate(QuoteItemBase):
    """Schema for quote item creation."""
    element_id: Optional[UUID] = Field(None, description="Related construction element")
    
    class Config:
        schema_extra = {
            "example": {
                "description": "Foundation concrete work",
                "category": "Foundation",
                "material_cost_min": 12000.0,
                "material_cost_max": 15000.0,
                "labor_cost_min": 8000.0,
                "labor_cost_max": 10000.0,
                "equipment_cost_min": 3000.0,
                "equipment_cost_max": 4000.0,
                "time_estimate_min": 80.0,
                "time_estimate_max": 100.0,
                "notes": "Includes reinforced concrete and necessary rebar",
                "element_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }
        }


class QuoteItemUpdate(BaseModel):
    """Schema for quote item updates."""
    description: Optional[str] = None
    category: Optional[str] = None
    material_cost_min: Optional[float] = None
    material_cost_max: Optional[float] = None
    labor_cost_min: Optional[float] = None
    labor_cost_max: Optional[float] = None
    equipment_cost_min: Optional[float] = None
    equipment_cost_max: Optional[float] = None
    time_estimate_min: Optional[float] = None
    time_estimate_max: Optional[float] = None
    notes: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    element_id: Optional[UUID] = None


class QuoteItemInDBBase(QuoteItemBase):
    """Quote item schema with DB fields."""
    id: UUID
    quote_id: UUID
    element_id: Optional[UUID]
    
    class Config:
        orm_mode = True


class QuoteItem(QuoteItemInDBBase):
    """Quote item response schema."""
    pass


class QuoteBase(BaseModel):
    """Base quote schema."""
    name: Optional[str] = Field(None, description="Quote name")
    description: Optional[str] = Field(None, description="Quote description")
    region: Optional[str] = Field(None, description="Geographic region for cost adjustments")
    version: Optional[str] = Field("1.0", description="Quote version")
    status: Optional[str] = Field("draft", description="Quote status")
    total_min: Optional[float] = Field(0.0, description="Minimum total cost")
    total_max: Optional[float] = Field(0.0, description="Maximum total cost")
    currency: Optional[str] = Field("USD", description="Currency code")
    notes: Optional[str] = Field(None, description="Additional notes")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Client preferences")


class QuoteCreate(QuoteBase):
    """Schema for quote creation."""
    project_id: Optional[UUID] = Field(None, description="Related project")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Commercial Building Renovation Quote",
                "description": "Cost estimate for the renovation project",
                "region": "Northeast US",
                "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "preferences": {
                    "sustainable_materials": True,
                    "premium_finishes": False
                }
            }
        }


class QuoteUpdate(BaseModel):
    """Schema for quote updates."""
    name: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    total_min: Optional[float] = None
    total_max: Optional[float] = None
    currency: Optional[str] = None
    notes: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    project_id: Optional[UUID] = None


class QuoteInDBBase(QuoteBase):
    """Quote schema with DB fields."""
    id: UUID
    owner_id: UUID
    project_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Quote(QuoteInDBBase):
    """Quote response schema."""
    items: Optional[List[QuoteItem]] = []
    
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Commercial Building Renovation Quote",
                "description": "Cost estimate for the renovation project",
                "region": "Northeast US",
                "version": "1.0",
                "status": "draft",
                "total_min": 150000.0,
                "total_max": 180000.0,
                "currency": "USD",
                "notes": "This quote includes all labor, materials, and equipment",
                "preferences": {
                    "sustainable_materials": True,
                    "premium_finishes": False
                },
                "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_at": "2025-03-24T12:34:56",
                "updated_at": "2025-03-24T12:34:56",
                "items": []
            }
        }
