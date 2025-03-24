from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Shared properties
class DocumentBase(BaseModel):
    filename: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    project_id: Optional[int] = None

# Properties to receive via API on creation/upload
class DocumentCreate(DocumentBase):
    pass

# Properties to receive via API on update
class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    project_id: Optional[int] = None
    is_analyzed: Optional[bool] = None
    analysis_status: Optional[str] = None

# Properties shared by models stored in DB
class DocumentInDBBase(DocumentBase):
    id: int
    is_analyzed: bool
    analysis_status: str
    upload_date: datetime
    analysis_date: Optional[datetime] = None
    uploaded_by: int

    class Config:
        orm_mode = True

# Properties to return via API
class Document(DocumentInDBBase):
    pass

# Document specification
class DocumentSpecificationBase(BaseModel):
    category: str
    key: str
    value: str
    document_id: int

# Properties to receive via API on creation
class DocumentSpecificationCreate(DocumentSpecificationBase):
    pass

# Properties shared by models stored in DB
class DocumentSpecificationInDBBase(DocumentSpecificationBase):
    id: int

    class Config:
        orm_mode = True

# Properties to return via API
class DocumentSpecification(DocumentSpecificationInDBBase):
    pass

# Document with specifications
class DocumentWithSpecs(Document):
    specifications: Optional[Dict[str, Any]] = None

# Document analysis request
class DocumentAnalysisRequest(BaseModel):
    file_path: str
    project_id: Optional[int] = None

# Document analysis response
class DocumentAnalysisResponse(BaseModel):
    document_id: int
    is_analyzed: bool
    analysis_status: str
    elements: Optional[List[Any]] = []
    specifications: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None