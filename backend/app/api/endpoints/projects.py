"""
Project management API endpoints.
"""
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from ...core.security import get_current_user
from ...db import models
from ...db.session import get_db
from ...schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter()


@router.get("/", response_model=List[Project])
def read_projects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter projects by status"),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve projects for the current user.
    """
    query = db.query(models.Project).filter(models.Project.owner_id == current_user.id)
    
    # Apply status filter if provided
    if status:
        query = query.filter(models.Project.status == status)
    
    # Apply pagination
    projects = query.offset(skip).limit(limit).all()
    
    return projects


@router.post("/", response_model=Project)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new project.
    """
    # Create project
    project = models.Project(
        **project_in.dict(),
        owner_id=current_user.id
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.get("/{project_id}", response_model=Project)
def read_project(
    *,
    db: Session = Depends(get_db),
    project_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get project by ID.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.put("/{project_id}", response_model=Project)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: UUID4,
    project_in: ProjectUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update project.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update project
    update_data = project_in.dict(exclude_unset=True)
    
    # Update fields
    for field in update_data:
        setattr(project, field, update_data[field])
    
    # Always update the updated_at timestamp
    project.updated_at = datetime.utcnow()
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", response_model=Project)
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete project.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
    
    return project


@router.get("/{project_id}/documents", response_model=List)
def read_project_documents(
    *,
    db: Session = Depends(get_db),
    project_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get all documents for a project.
    """
    # Verify user has access to the project
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get documents
    documents = db.query(models.Document).filter(
        models.Document.project_id == project_id
    ).all()
    
    return documents


@router.get("/{project_id}/elements", response_model=List)
def read_project_elements(
    *,
    db: Session = Depends(get_db),
    project_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get all construction elements for a project.
    """
    # Verify user has access to the project
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get elements
    elements = db.query(models.Element).filter(
        models.Element.project_id == project_id
    ).all()
    
    return elements


@router.get("/{project_id}/quotes", response_model=List)
def read_project_quotes(
    *,
    db: Session = Depends(get_db),
    project_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get all quotes for a project.
    """
    # Verify user has access to the project
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get quotes
    quotes = db.query(models.Quote).filter(
        models.Quote.project_id == project_id
    ).all()
    
    return quotes
