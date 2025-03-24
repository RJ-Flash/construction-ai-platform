from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base

class MaterialCategory(str, enum.Enum):
    STRUCTURAL = "structural"
    FINISHES = "finishes"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    SITE_WORK = "site_work"
    EQUIPMENT = "equipment"
    OTHER = "other"

class MaterialUnit(str, enum.Enum):
    SQUARE_FEET = "sq_ft"
    SQUARE_METER = "sq_m"
    CUBIC_YARD = "cu_yd"
    CUBIC_METER = "cu_m"
    LINEAR_FEET = "ln_ft"
    LINEAR_METER = "ln_m"
    EACH = "each"
    POUND = "lb"
    KILOGRAM = "kg"
    TON = "ton"
    GALLON = "gal"
    LITER = "L"
    HOUR = "hr"
    DAY = "day"

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(MaterialCategory), default=MaterialCategory.OTHER)
    unit = Column(Enum(MaterialUnit), nullable=False)
    unit_cost = Column(Float, nullable=False)
    labor_rate = Column(Float, nullable=True)  # Cost per unit of labor
    equipment_rate = Column(Float, nullable=True)  # Cost per unit of equipment
    overhead_percent = Column(Float, default=10.0)  # Overhead percentage
    profit_percent = Column(Float, default=15.0)  # Profit percentage
    is_custom = Column(Boolean, default=False)
    
    # Relationships
    elements = relationship("ElementMaterial", back_populates="material")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Material {self.id}: {self.name}>"
