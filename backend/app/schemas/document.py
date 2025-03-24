from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.db.models.document import DocumentType, DocumentStatus

class DocumentBase(BaseModel):
    original_filename: Optional[str] = None
    document_type: Optional[str] = None
    notes: Optional[str] = None

    @validator("document_type")
    def validate_document_type(cls, v):
        if v is not None and v not in [doc_type.value for doc_type in DocumentType]:
            raise ValueError(f"Invalid document_type. Must be one of: {', '.join([doc_type.value for doc_type in DocumentType])}")
        return v

class DocumentCreate(DocumentBase):
    project_id: int
    original_filename: str
    file_path: str
    file_size: int
    file_type: str

class DocumentUpdate(DocumentBase):
    document_type: Optional[str] = None
    status: Optional[str] = None
    confidence_score: Optional[float] = None
    scale_factor: Optional[float] = None
    notes: Optional[str] = None
    
    @validator("status")
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in DocumentStatus]:
            raise ValueError(f"Invalid status. Must be one of: {', '.join([status.value for status in DocumentStatus])}")
        return v

class DocumentInDBBase(DocumentBase):
    id: int
    filename: str
    file_path: str
    file_size: int
    file_type: str
    document_type: str
    status: str
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    scale_factor: Optional[float] = None
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class DocumentResponse(DocumentInDBBase):
    element_count: Optional[int] = None
