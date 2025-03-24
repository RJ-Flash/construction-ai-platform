from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import project_service

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new project.
    """
    return project_service.create_project(db=db, project_in=project_in, user_id=current_user.id)

@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    *,
    db: Session = Depends(deps.get_db),
    status: Optional[str] = Query(None, description="Filter by project status"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get list of projects.
    """
    if current_user.role == "admin":
        # Admins can see all projects
        return project_service.get_projects(db=db, status=status, skip=skip, limit=limit)
    else:
        # Regular users can only see their own projects
        return project_service.get_user_projects(
            db=db, user_id=current_user.id, status=status, skip=skip, limit=limit
        )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get project by ID.
    """
    project = project_service.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to the project
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update project information.
    """
    project = project_service.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to the project
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    project = project_service.update_project(db=db, project=project, project_in=project_in)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a project.
    """
    project = project_service.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to the project
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    project_service.delete_project(db=db, project_id=project_id)
    return None

@router.get("/{project_id}/summary", response_model=dict)
def get_project_summary(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get project summary including document count, element count, and estimation totals.
    """
    project = project_service.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to the project
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return project_service.get_project_summary(db=db, project_id=project_id)
