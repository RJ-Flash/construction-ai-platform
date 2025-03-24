import os
import time
import uuid
import shutil
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.db.models.document import Document, DocumentStatus, DocumentType
from app.db.models.project import Project
from app.db.models.element import Element
from app.schemas.document import DocumentCreate, DocumentUpdate

from .document_classifier import classify_document
from .pdf_processor import process_pdf
from .cad_processor import process_cad
from .bim_processor import process_bim

class DocumentService:
    def get_document(self, db: Session, document_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.id == document_id).first()

    def get_documents_by_project(
        self, 
        db: Session, 
        project_id: int,
        status: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> List[Document]:
        query = db.query(Document).filter(Document.project_id == project_id)
        
        if status:
            query = query.filter(Document.status == status)
            
        if document_type:
            query = query.filter(Document.document_type == document_type)
            
        return query.all()

    async def upload_document(self, db: Session, file: UploadFile, project_id: int, current_user=None) -> Document:
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
            
        # Check if file is allowed
        file_ext = os.path.splitext(file.filename)[1].lower().replace(".", "")
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Create upload directory if it doesn't exist
        os.makedirs(os.path.join(settings.UPLOAD_FOLDER, str(project_id)), exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(project_id), unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create document record
        document_in = DocumentCreate(
            project_id=project_id,
            original_filename=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_type=file_ext
        )
        
        document = Document(
            **document_in.dict(),
            filename=unique_filename,
            status=DocumentStatus.UPLOADED
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document

    def process_document(self, db: Session, document: Document) -> Document:
        """
        Process a document using appropriate processor based on file type
        """
        if document.status not in [DocumentStatus.UPLOADED, DocumentStatus.FAILED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document cannot be processed in '{document.status}' status"
            )
        
        # Update status to processing
        document.status = DocumentStatus.PROCESSING
        db.add(document)
        db.commit()
        
        # Record start time for processing metrics
        start_time = time.time()
        
        try:
            # Process document based on file type
            if document.file_type.lower() == 'pdf':
                result = process_pdf(document.file_path)
            elif document.file_type.lower() in ['dwg', 'dxf']:
                result = process_cad(document.file_path)
            elif document.file_type.lower() in ['ifc', 'rvt']:
                result = process_bim(document.file_path)
            else:
                raise ValueError(f"Unsupported file type: {document.file_type}")
            
            # Attempt to classify document if not already classified
            if document.document_type == DocumentType.OTHER:
                document_type = classify_document(document.file_path, result.get('text', ''))
                document.document_type = document_type
            
            # Update document with processing results
            document.status = DocumentStatus.ANALYZED
            document.confidence_score = result.get('confidence_score', None)
            document.scale_factor = result.get('scale_factor', None)
            document.processing_time = time.time() - start_time
            
            # Save elements detected in the document
            if 'elements' in result:
                for element_data in result.get('elements', []):
                    element = Element(**element_data, document_id=document.id)
                    db.add(element)
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            return document
            
        except Exception as e:
            # Update status to failed if processing fails
            document.status = DocumentStatus.FAILED
            document.notes = f"Processing failed: {str(e)}"
            db.add(document)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {str(e)}"
            )

    def update_document(self, db: Session, document: Document, document_in: DocumentUpdate) -> Document:
        update_data = document_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(document, field, value)
            
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def delete_document(self, db: Session, document_id: int) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            # Try to delete the file
            if os.path.exists(document.file_path):
                try:
                    os.remove(document.file_path)
                except Exception:
                    pass  # Ignore file deletion errors
                    
            db.delete(document)
            db.commit()
