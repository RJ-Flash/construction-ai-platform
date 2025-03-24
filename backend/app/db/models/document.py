from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base

class DocumentType(str, enum.Enum):
    ARCHITECTURAL = "architectural"
    STRUCTURAL = "structural"
    MEP = "mep"
    OTHER = "other"

class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    scale_factor = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="documents")
    elements = relationship("Element", back_populates="document", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Document {self.id}: {self.original_filename}>"
