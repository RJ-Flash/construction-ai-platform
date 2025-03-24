from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime

from ...db.database import get_db
from ...db.models import Document, Project
from ...schemas import (
    Document as DocumentSchema, 
    DocumentCreate, 
    DocumentUpdate, 
    DocumentWithSpecs,
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    User as UserSchema
)
from ...core.auth import get_current_active_user
from ...core.config import settings
from ...services.document_analysis import DocumentAnalysisService

router = APIRouter()

@router.get("/", response_model=List[DocumentSchema])
async def read_documents(
    skip: int = 0, 
    limit: int = 100,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve all documents, optionally filtered by project.
    """
    query = db.query(Document)
    
    # Filter by project if specified
    if project_id:
        # Verify project exists and user has access
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")
            
        query = query.filter(Document.project_id == project_id)
    else:
        # If no project specified, show documents from projects user has access to
        query = query.join(Project).filter(
            (Project.owner_id == current_user.id) | 
            (Project.users.any(id=current_user.id))
        )
    
    documents = query.order_by(Document.upload_date.desc()).offset(skip).limit(limit).all()
    return documents

@router.post("/upload", response_model=DocumentSchema, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Upload a new document.
    """
    # Verify project if provided
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.DOCUMENT_UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.DOCUMENT_UPLOAD_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Get file type from extension
    _, file_extension = os.path.splitext(file.filename)
    file_type = file_extension.lstrip('.').upper()
    
    # Create document in database
    db_document = Document(
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        project_id=project_id,
        uploaded_by=current_user.id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("/{document_id}", response_model=DocumentWithSpecs)
async def read_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get details of a specific document, including specifications.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to the project this document belongs to
    if document.project_id:
        project = db.query(Project).filter(Project.id == document.project_id).first()
        if project and project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    # Convert specifications to dictionary format
    specs_dict = {}
    for spec in document.specifications:
        if spec.category not in specs_dict:
            specs_dict[spec.category] = []
        specs_dict[spec.category].append(spec.value)
    
    # Create response object
    result = DocumentWithSpecs.from_orm(document)
    result.specifications = specs_dict
    
    return result

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Delete a document.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to the project this document belongs to
    if document.project_id:
        project = db.query(Project).filter(Project.id == document.project_id).first()
        if project and project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this document")
    
    # Delete the physical file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log the error but continue with database deletion
        print(f"Error deleting file: {e}")
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return None

# Function for background task
async def analyze_document_task(document_id: int, db: Session):
    """
    Background task to analyze a document.
    """
    service = DocumentAnalysisService(db)
    await service.analyze_document(document_id)

@router.post("/analyze", response_model=DocumentSchema)
async def trigger_document_analysis(
    analysis_request: DocumentAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Trigger analysis for a document. The analysis will run in the background.
    """
    # Verify the file exists
    document = db.query(Document).filter(Document.file_path == analysis_request.file_path).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to the project this document belongs to
    if document.project_id:
        project = db.query(Project).filter(Project.id == document.project_id).first()
        if project and project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to analyze this document")
    
    # Update document project if provided
    if analysis_request.project_id and analysis_request.project_id != document.project_id:
        # Verify project exists and user has access
        project = db.query(Project).filter(Project.id == analysis_request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")
            
        document.project_id = analysis_request.project_id
        db.commit()
    
    # Check if document is already being analyzed
    if document.analysis_status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Document is already being analyzed"
        )
    
    # Update document status
    document.analysis_status = "pending"
    db.commit()
    
    # Add analysis task to background tasks
    background_tasks.add_task(analyze_document_task, document.id, db)
    
    return document

@router.get("/{document_id}/elements", response_model=List)
async def read_document_elements(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get elements extracted from a document.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user has access to the project this document belongs to
    if document.project_id:
        project = db.query(Project).filter(Project.id == document.project_id).first()
        if project and project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    return document.elements