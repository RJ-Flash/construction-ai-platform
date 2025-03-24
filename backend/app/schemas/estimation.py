from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.db.models.estimation import EstimationStatus

class EstimationBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    @validator("status")
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in EstimationStatus]:
            raise ValueError(f"Invalid status. Must be one of: {', '.join([status.value for status in EstimationStatus])}")
        return v

class EstimationCreate(EstimationBase):
    name: str
    project_id: int
    material_cost: Optional[float] = 0.0
    labor_cost: Optional[float] = 0.0
    equipment_cost: Optional[float] = 0.0
    overhead_cost: Optional[float] = 0.0
    profit_amount: Optional[float] = 0.0
    total_cost: Optional[float] = 0.0
    cost_breakdown: Optional[Dict[str, Any]] = None
    element_costs: Optional[Dict[str, Any]] = None

class EstimationUpdate(EstimationBase):
    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    equipment_cost: Optional[float] = None
    overhead_cost: Optional[float] = None
    profit_amount: Optional[float] = None
    total_cost: Optional[float] = None
    cost_breakdown: Optional[Dict[str, Any]] = None
    element_costs: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None

class EstimationInDBBase(EstimationBase):
    id: int
    project_id: int
    material_cost: float
    labor_cost: float
    equipment_cost: float
    overhead_cost: float
    profit_amount: float
    total_cost: float
    confidence_score: Optional[float] = None
    estimation_time: Optional[float] = None
    cost_breakdown: Optional[Dict[str, Any]] = None
    element_costs: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class EstimationResponse(EstimationInDBBase):
    pass
