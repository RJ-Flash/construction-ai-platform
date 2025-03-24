from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import Element, Project, Document, User
from ...schemas import elements as schemas
from ...core.security import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Element])
def read_elements(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    document_id: Optional[int] = None,
    element_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve elements with optional filtering by project, document, or type.
    """
    query = db.query(Element)
    
    # Filter by project if specified
    if project_id:
        # Verify project exists and user has access
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")
            
        query = query.filter(Element.project_id == project_id)
    else:
        # If no project specified, show elements from projects user has access to
        query = query.join(Project, Element.project_id == Project.id).filter(
            (Project.owner_id == current_user.id) | 
            (Project.users.any(id=current_user.id))
        )
    
    # Filter by document if specified
    if document_id:
        query = query.filter(Element.document_id == document_id)
    
    # Filter by element type if specified
    if element_type:
        query = query.filter(Element.type == element_type)
    
    elements = query.offset(skip).limit(limit).all()
    return elements

@router.get("/{element_id}", response_model=schemas.Element)
def read_element(
    element_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific element by ID.
    """
    element = db.query(Element).filter(Element.id == element_id).first()
    
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Check if user has access to the project this element belongs to
    if element.project_id:
        project = db.query(Project).filter(Project.id == element.project_id).first()
        if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this element")
    
    return element

@router.post("/", response_model=schemas.Element)
def create_element(
    element: schemas.ElementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new element.
    """
    # Verify project if provided
    if element.project_id:
        project = db.query(Project).filter(Project.id == element.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Verify document if provided
    if element.document_id:
        document = db.query(Document).filter(Document.id == element.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # If the document belongs to a project, check access
        if document.project_id:
            project = db.query(Project).filter(Project.id == document.project_id).first()
            if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
                raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    # Create the element
    db_element = Element(**element.dict())
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    
    return db_element

@router.put("/{element_id}", response_model=schemas.Element)
def update_element(
    element_id: int,
    element: schemas.ElementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing element.
    """
    db_element = db.query(Element).filter(Element.id == element_id).first()
    
    if not db_element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Check if user has access to the project this element belongs to
    if db_element.project_id:
        project = db.query(Project).filter(Project.id == db_element.project_id).first()
        if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to update this element")
    
    # Update element with new data
    update_data = element.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_element, key, value)
    
    # If project_id is changing, verify access to new project
    if 'project_id' in update_data and update_data['project_id'] != db_element.project_id:
        new_project = db.query(Project).filter(Project.id == update_data['project_id']).first()
        if not new_project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if new_project.owner_id != current_user.id and current_user.id not in [u.id for u in new_project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access the target project")
    
    db.commit()
    db.refresh(db_element)
    
    return db_element

@router.delete("/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_element(
    element_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an element.
    """
    db_element = db.query(Element).filter(Element.id == element_id).first()
    
    if not db_element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Check if user has access to the project this element belongs to
    if db_element.project_id:
        project = db.query(Project).filter(Project.id == db_element.project_id).first()
        if project and project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this element")
    
    db.delete(db_element)
    db.commit()
    
    return None

@router.get("/types/", response_model=List[str])
def get_element_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of all distinct element types in the system.
    """
    # Get all projects user has access to
    user_projects = db.query(Project).filter(
        (Project.owner_id == current_user.id) | 
        (Project.users.any(id=current_user.id))
    ).all()
    
    project_ids = [project.id for project in user_projects]
    
    # Query distinct element types from accessible projects
    element_types = db.query(Element.type)\
        .filter(Element.project_id.in_(project_ids))\
        .distinct()\
        .all()
    
    return [elem_type[0] for elem_type in element_types if elem_type[0]]

@router.get("/statistics/", response_model=schemas.ElementStatistics)
def get_element_statistics(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistics about elements, optionally filtered by project.
    """
    query = db.query(Element)
    
    # Filter by project if specified
    if project_id:
        # Verify project exists and user has access
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")
            
        query = query.filter(Element.project_id == project_id)
    else:
        # If no project specified, show elements from projects user has access to
        query = query.join(Project, Element.project_id == Project.id).filter(
            (Project.owner_id == current_user.id) | 
            (Project.users.any(id=current_user.id))
        )
    
    # Get total count
    total_count = query.count()
    
    # Get count by type
    type_counts = {}
    element_types = db.query(Element.type).filter(Element.id.in_([e.id for e in query])).distinct().all()
    
    for elem_type in element_types:
        if elem_type[0]:  # Skip None types
            count = query.filter(Element.type == elem_type[0]).count()
            type_counts[elem_type[0]] = count
    
    # Calculate total estimated price
    total_price = 0
    elements_with_price = query.filter(Element.estimated_price.isnot(None)).all()
    
    for element in elements_with_price:
        total_price += (element.estimated_price or 0) * (element.quantity or 1)
    
    return {
        "total_count": total_count,
        "type_counts": type_counts,
        "total_estimated_price": total_price
    }
