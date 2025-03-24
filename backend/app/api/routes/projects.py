from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from ...db.database import get_db
from ...db.models import Project, Document, Element, Quote, User
from ...schemas import (
    Project as ProjectSchema, 
    ProjectCreate, 
    ProjectUpdate, 
    ProjectList,
    ProjectDetail,
    ProjectStats,
    User as UserSchema
)
from ...core.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[ProjectList])
async def read_projects(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve all projects accessible by the current user.
    """
    query = db.query(Project).filter(
        (Project.owner_id == current_user.id) | 
        (Project.users.any(User.id == current_user.id))
    )
    
    if status:
        query = query.filter(Project.status == status)
        
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Create a new project.
    """
    db_project = Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectDetail)
async def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get details of a specific project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check if user has access to the project
    if project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Get counts for details
    document_count = db.query(func.count(Document.id)).filter(Document.project_id == project_id).scalar() or 0
    element_count = db.query(func.count(Element.id)).filter(Element.project_id == project_id).scalar() or 0
    quote_count = db.query(func.count(Quote.id)).filter(Quote.project_id == project_id).scalar() or 0
    
    result = ProjectDetail.from_orm(project)
    result.document_count = document_count
    result.element_count = element_count
    result.quote_count = quote_count
    
    return result

@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Update a project.
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check if user is the owner
    if db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")
    
    # Update fields if provided
    for field, value in project_update.dict(exclude_unset=True).items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Delete a project.
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check if user is the owner
    if db_project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    db.delete(db_project)
    db.commit()
    
    return None

@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get statistics for a project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check if user has access to the project
    if project.owner_id != current_user.id and current_user.id not in [user.id for user in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Get document stats
    total_documents = db.query(func.count(Document.id)).filter(Document.project_id == project_id).scalar() or 0
    analyzed_documents = db.query(func.count(Document.id)).filter(
        Document.project_id == project_id,
        Document.is_analyzed == True
    ).scalar() or 0
    
    # Get element stats
    total_elements = db.query(func.count(Element.id)).filter(Element.project_id == project_id).scalar() or 0
    
    # Get quote stats
    quotes_by_status = {}
    for status_name in ["draft", "sent", "accepted", "declined"]:
        count = db.query(func.count(Quote.id)).filter(
            Quote.project_id == project_id,
            Quote.status == status_name
        ).scalar() or 0
        quotes_by_status[status_name] = count
    
    # Get total quote value
    total_value = db.query(func.sum(Quote.total_amount)).filter(
        Quote.project_id == project_id,
        Quote.status.in_(["accepted", "sent"])
    ).scalar() or 0
    
    return ProjectStats(
        total_documents=total_documents,
        analyzed_documents=analyzed_documents,
        total_elements=total_elements,
        quotes_count=quotes_by_status,
        total_value=total_value
    )