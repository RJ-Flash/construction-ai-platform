from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.project import Project
from app.db.models.document import Document
from app.db.models.estimation import Estimation
from app.db.models.element import Element
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    def get_project(self, db: Session, project_id: int) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    def get_projects(self, db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Project]:
        query = db.query(Project)
        if status:
            query = query.filter(Project.status == status)
        return query.offset(skip).limit(limit).all()

    def get_user_projects(self, db: Session, user_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Project]:
        query = db.query(Project).filter(Project.user_id == user_id)
        if status:
            query = query.filter(Project.status == status)
        return query.offset(skip).limit(limit).all()

    def create_project(self, db: Session, project_in: ProjectCreate, user_id: int) -> Project:
        project = Project(
            **project_in.dict(),
            user_id=user_id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update_project(self, db: Session, project: Project, project_in: ProjectUpdate) -> Project:
        update_data = project_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def delete_project(self, db: Session, project_id: int) -> None:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            db.delete(project)
            db.commit()

    def get_project_summary(self, db: Session, project_id: int) -> Dict[str, Any]:
        # Get document count
        document_count = db.query(func.count(Document.id)).filter(Document.project_id == project_id).scalar()
        
        # Get estimation count
        estimation_count = db.query(func.count(Estimation.id)).filter(Estimation.project_id == project_id).scalar()
        
        # Get element count across all documents
        element_count = db.query(func.count(Element.id)).join(Document).filter(Document.project_id == project_id).scalar()
        
        # Get latest estimation if any
        latest_estimation = db.query(Estimation).filter(Estimation.project_id == project_id).order_by(Estimation.created_at.desc()).first()
        
        # Calculate element type distribution
        element_distribution = {}
        if element_count > 0:
            element_types = db.query(Element.element_type, func.count(Element.id))\
                .join(Document)\
                .filter(Document.project_id == project_id)\
                .group_by(Element.element_type)\
                .all()
            element_distribution = {e_type: count for e_type, count in element_types}
            
        return {
            "document_count": document_count,
            "estimation_count": estimation_count,
            "element_count": element_count,
            "element_distribution": element_distribution,
            "latest_estimation": latest_estimation.total_cost if latest_estimation else None,
            "estimation_status": latest_estimation.status if latest_estimation else None
        }

project_service = ProjectService()
