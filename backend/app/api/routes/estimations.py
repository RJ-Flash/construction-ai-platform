from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.db.models.user import User
from app.schemas.estimation import EstimationCreate, EstimationResponse, EstimationUpdate
from app.services.estimation import estimation_service

router = APIRouter()

@router.post("/", response_model=EstimationResponse, status_code=status.HTTP_201_CREATED)
def create_estimation(
    *,
    db: Session = Depends(deps.get_db),
    estimation_in: EstimationCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new estimation manually.
    """
    return estimation_service.create_estimation(db=db, estimation_in=estimation_in)

@router.post("/generate/{project_id}", response_model=EstimationResponse)
def generate_estimation(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate an automatic estimation for a project based on AI analysis.
    """
    return estimation_service.generate_estimation(db=db, project_id=project_id)

@router.get("/project/{project_id}", response_model=List[EstimationResponse])
def get_project_estimations(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    status: Optional[str] = Query(None, description="Filter by estimation status"),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get all estimations for a project.
    """
    return estimation_service.get_estimations_by_project(
        db=db,
        project_id=project_id,
        status=status
    )

@router.get("/{estimation_id}", response_model=EstimationResponse)
def get_estimation(
    *,
    db: Session = Depends(deps.get_db),
    estimation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get estimation by ID.
    """
    estimation = estimation_service.get_estimation(db=db, estimation_id=estimation_id)
    if not estimation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimation not found"
        )
    return estimation

@router.put("/{estimation_id}", response_model=EstimationResponse)
def update_estimation(
    *,
    db: Session = Depends(deps.get_db),
    estimation_id: int,
    estimation_in: EstimationUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update estimation.
    """
    estimation = estimation_service.get_estimation(db=db, estimation_id=estimation_id)
    if not estimation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimation not found"
        )
    
    estimation = estimation_service.update_estimation(db=db, estimation=estimation, estimation_in=estimation_in)
    return estimation

@router.post("/{estimation_id}/finalize", response_model=EstimationResponse)
def finalize_estimation(
    *,
    db: Session = Depends(deps.get_db),
    estimation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Change estimation status to finalized.
    """
    estimation = estimation_service.get_estimation(db=db, estimation_id=estimation_id)
    if not estimation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimation not found"
        )
    
    if estimation.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft estimations can be finalized"
        )
    
    estimation_in = EstimationUpdate(status="finalized")
    estimation = estimation_service.update_estimation(db=db, estimation=estimation, estimation_in=estimation_in)
    return estimation

@router.post("/{estimation_id}/approve", response_model=EstimationResponse)
def approve_estimation(
    *,
    db: Session = Depends(deps.get_db),
    estimation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Approve an estimation (change status to approved).
    """
    estimation = estimation_service.get_estimation(db=db, estimation_id=estimation_id)
    if not estimation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimation not found"
        )
    
    if estimation.status != "finalized":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only finalized estimations can be approved"
        )
    
    estimation_in = EstimationUpdate(status="approved")
    estimation = estimation_service.update_estimation(db=db, estimation=estimation, estimation_in=estimation_in)
    return estimation

@router.post("/{estimation_id}/reject", response_model=EstimationResponse)
def reject_estimation(
    *,
    db: Session = Depends(deps.get_db),
    estimation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Reject an estimation (change status to rejected).
    """
    estimation = estimation_service.get_estimation(db=db, estimation_id=estimation_id)
    if not estimation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimation not found"
        )
    
    if estimation.status != "finalized":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only finalized estimations can be rejected"
        )
    
    estimation_in = EstimationUpdate(status="rejected")
    estimation = estimation_service.update_estimation(db=db, estimation=estimation, estimation_in=estimation_in)
    return estimation

@router.delete("/{estimation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estimation(
    *,
    db: Session = Depends(deps.get_db),
    estimation_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete an estimation.
    """
    estimation = estimation_service.get_estimation(db=db, estimation_id=estimation_id)
    if not estimation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estimation not found"
        )
    
    estimation_service.delete_estimation(db=db, estimation_id=estimation_id)
    return None
