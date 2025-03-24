from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base

class ElementType(str, enum.Enum):
    WALL = "wall"
    COLUMN = "column"
    BEAM = "beam"
    DOOR = "door"
    WINDOW = "window"
    CEILING = "ceiling"
    FLOOR = "floor"
    ROOF = "roof"
    STAIR = "stair"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    ANNOTATION = "annotation"
    OTHER = "other"

class Element(Base):
    __tablename__ = "elements"
    
    id = Column(Integer, primary_key=True, index=True)
    element_type = Column(Enum(ElementType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Geometric properties
    coordinates = Column(JSON, nullable=True)  # Stored as a GeoJSON object
    length = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    area = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    quantity = Column(Integer, default=1)
    
    # Detection metadata
    confidence_score = Column(Float, nullable=True)
    detection_method = Column(String(50), nullable=True)
    
    # Relationships
    document_id = Column(Integer, ForeignKey("documents.id"))
    document = relationship("Document", back_populates="elements")
    materials = relationship("ElementMaterial", back_populates="element", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Element {self.id}: {self.element_type} - {self.name}>"


class ElementMaterial(Base):
    __tablename__ = "element_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    
    # Relationships
    element_id = Column(Integer, ForeignKey("elements.id"))
    element = relationship("Element", back_populates="materials")
    material_id = Column(Integer, ForeignKey("materials.id"))
    material = relationship("Material", back_populates="elements")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ElementMaterial {self.id}: {self.element_id} - {self.material_id}>"
