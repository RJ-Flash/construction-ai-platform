from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.db.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.document import document_service

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    project_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Upload a construction document (PDF, CAD, BIM) for processing.
    """
    return await document_service.upload_document(db=db, file=file, project_id=project_id, current_user=current_user)

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get document by ID.
    """
    document = document_service.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.get("/project/{project_id}", response_model=List[DocumentResponse])
def get_project_documents(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    status: Optional[str] = Query(None, description="Filter by document status"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get all documents in a project.
    """
    return document_service.get_documents_by_project(
        db=db, 
        project_id=project_id,
        status=status,
        document_type=document_type
    )

@router.post("/{document_id}/process", response_model=DocumentResponse)
def process_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Process a document for AI analysis.
    """
    document = document_service.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Process the document and update its status
    return document_service.process_document(db=db, document=document)

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    document_in: DocumentUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update document information.
    """
    document = document_service.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    document = document_service.update_document(db=db, document=document, document_in=document_in)
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a document.
    """
    document = document_service.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    document_service.delete_document(db=db, document_id=document_id)
    return None
