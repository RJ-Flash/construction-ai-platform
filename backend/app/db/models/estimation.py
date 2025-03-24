from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base

class EstimationStatus(str, enum.Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"
    APPROVED = "approved"
    REJECTED = "rejected"

class Estimation(Base):
    __tablename__ = "estimations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(EstimationStatus), default=EstimationStatus.DRAFT)
    
    # Cost breakdown
    material_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    equipment_cost = Column(Float, default=0.0)
    overhead_cost = Column(Float, default=0.0)
    profit_amount = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Estimation metadata
    confidence_score = Column(Float, nullable=True)
    estimation_time = Column(Float, nullable=True)  # Time in seconds
    notes = Column(Text, nullable=True)
    
    # Detailed breakdown storage
    cost_breakdown = Column(JSON, nullable=True)  # Detailed cost breakdown by category
    element_costs = Column(JSON, nullable=True)  # Costs by element type
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="estimations")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Estimation {self.id}: {self.name} - ${self.total_cost:.2f}>"
