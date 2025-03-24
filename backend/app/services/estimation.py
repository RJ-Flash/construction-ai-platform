import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.db.models.estimation import Estimation, EstimationStatus
from app.db.models.project import Project
from app.db.models.document import Document, DocumentStatus
from app.db.models.element import Element, ElementType
from app.db.models.material import Material, ElementMaterial

from app.schemas.estimation import EstimationCreate, EstimationUpdate

# Set up logger
logger = logging.getLogger(__name__)

class EstimationService:
    def get_estimation(self, db: Session, estimation_id: int) -> Optional[Estimation]:
        """Get an estimation by ID."""
        return db.query(Estimation).filter(Estimation.id == estimation_id).first()
    
    def get_estimations_by_project(
        self, 
        db: Session, 
        project_id: int,
        status: Optional[str] = None
    ) -> List[Estimation]:
        """Get all estimations for a project."""
        query = db.query(Estimation).filter(Estimation.project_id == project_id)
        
        if status:
            query = query.filter(Estimation.status == status)
            
        return query.all()
    
    def create_estimation(self, db: Session, estimation_in: EstimationCreate) -> Estimation:
        """Create a new estimation manually."""
        # Check if project exists
        project = db.query(Project).filter(Project.id == estimation_in.project_id).first()
        if not project:
            raise ValueError(f"Project with ID {estimation_in.project_id} not found")
        
        # Create estimation record
        estimation = Estimation(**estimation_in.dict())
        
        db.add(estimation)
        db.commit()
        db.refresh(estimation)
        
        # Update project's total estimate
        project.total_estimate = estimation.total_cost
        db.add(project)
        db.commit()
        
        return estimation
    
    def generate_estimation(self, db: Session, project_id: int) -> Estimation:
        """
        Generate an automatic estimation for a project based on AI analysis of documents.
        This involves:
        1. Finding all analyzed documents in the project
        2. Extracting all elements from those documents
        3. Associating materials and calculating costs
        4. Creating a detailed estimation breakdown
        """
        # Record start time for estimation metrics
        start_time = time.time()
        
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get all analyzed documents for the project
        documents = db.query(Document).filter(
            Document.project_id == project_id,
            Document.status == DocumentStatus.ANALYZED
        ).all()
        
        if not documents:
            raise ValueError("No analyzed documents found for this project")
        
        # Get all elements from these documents
        elements = db.query(Element).filter(
            Element.document_id.in_([doc.id for doc in documents])
        ).all()
        
        if not elements:
            raise ValueError("No elements found in the project documents")
        
        # Initialize cost categories
        material_cost = 0.0
        labor_cost = 0.0
        equipment_cost = 0.0
        
        # Initialize detailed breakdowns
        cost_breakdown = {
            "by_element_type": {},
            "by_document": {},
            "by_material": {}
        }
        
        element_costs = {}
        
        # Process each element and calculate costs
        for element in elements:
            # Find or create element costs entry
            element_key = f"{element.element_type}:{element.id}"
            if element_key not in element_costs:
                element_costs[element_key] = {
                    "name": element.name,
                    "type": element.element_type,
                    "description": element.description,
                    "material_cost": 0.0,
                    "labor_cost": 0.0,
                    "equipment_cost": 0.0,
                    "total_cost": 0.0
                }
            
            # Get materials for this element
            element_materials = db.query(ElementMaterial).filter(
                ElementMaterial.element_id == element.id
            ).all()
            
            # If no materials are associated, estimate based on element type
            if not element_materials:
                element_materials = self._estimate_default_materials(db, element)
            
            # Calculate costs for this element
            element_material_cost = 0.0
            element_labor_cost = 0.0
            element_equipment_cost = 0.0
            
            for elem_material in element_materials:
                material = db.query(Material).filter(Material.id == elem_material.material_id).first()
                if material:
                    # Calculate material cost
                    material_quantity_cost = elem_material.quantity * material.unit_cost
                    element_material_cost += material_quantity_cost
                    
                    # Calculate labor cost if applicable
                    if material.labor_rate:
                        element_labor_cost += elem_material.quantity * material.labor_rate
                    
                    # Calculate equipment cost if applicable
                    if material.equipment_rate:
                        element_equipment_cost += elem_material.quantity * material.equipment_rate
                    
                    # Update material breakdown
                    material_key = material.name
                    if material_key not in cost_breakdown["by_material"]:
                        cost_breakdown["by_material"][material_key] = 0.0
                    cost_breakdown["by_material"][material_key] += material_quantity_cost
            
            # Update element costs
            element_costs[element_key]["material_cost"] = element_material_cost
            element_costs[element_key]["labor_cost"] = element_labor_cost
            element_costs[element_key]["equipment_cost"] = element_equipment_cost
            element_costs[element_key]["total_cost"] = (
                element_material_cost + element_labor_cost + element_equipment_cost
            )
            
            # Add to running totals
            material_cost += element_material_cost
            labor_cost += element_labor_cost
            equipment_cost += element_equipment_cost
            
            # Update element type breakdown
            element_type = element.element_type
            if element_type not in cost_breakdown["by_element_type"]:
                cost_breakdown["by_element_type"][element_type] = 0.0
            cost_breakdown["by_element_type"][element_type] += element_costs[element_key]["total_cost"]
            
            # Update document breakdown
            doc_id = element.document_id
            if str(doc_id) not in cost_breakdown["by_document"]:
                doc = db.query(Document).filter(Document.id == doc_id).first()
                doc_name = doc.original_filename if doc else f"Document {doc_id}"
                cost_breakdown["by_document"][str(doc_id)] = {
                    "name": doc_name,
                    "cost": 0.0
                }
            cost_breakdown["by_document"][str(doc_id)]["cost"] += element_costs[element_key]["total_cost"]
        
        # Calculate overhead and profit
        # Default to industry standard percentages if not specified
        overhead_percent = 10.0  # 10% overhead
        profit_percent = 15.0    # 15% profit
        
        overhead_cost = (material_cost + labor_cost + equipment_cost) * (overhead_percent / 100)
        profit_amount = (material_cost + labor_cost + equipment_cost + overhead_cost) * (profit_percent / 100)
        total_cost = material_cost + labor_cost + equipment_cost + overhead_cost + profit_amount
        
        # Create an estimation name based on project and timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        estimation_name = f"{project.name} Estimation {timestamp}"
        
        # Calculate average confidence score
        confidence_score = sum([element.confidence_score for element in elements if element.confidence_score]) / len(elements) if elements else 0.7
        
        # Create the estimation record
        estimation_in = EstimationCreate(
            name=estimation_name,
            description=f"Auto-generated estimation for {project.name}",
            project_id=project_id,
            material_cost=material_cost,
            labor_cost=labor_cost,
            equipment_cost=equipment_cost,
            overhead_cost=overhead_cost,
            profit_amount=profit_amount,
            total_cost=total_cost,
            cost_breakdown=cost_breakdown,
            element_costs=element_costs,
            status=EstimationStatus.DRAFT
        )
        
        estimation = Estimation(**estimation_in.dict())
        estimation.confidence_score = confidence_score
        estimation.estimation_time = time.time() - start_time
        
        db.add(estimation)
        db.commit()
        db.refresh(estimation)
        
        # Update project's total estimate
        project.total_estimate = total_cost
        db.add(project)
        db.commit()
        
        return estimation
    
    def update_estimation(self, db: Session, estimation: Estimation, estimation_in: EstimationUpdate) -> Estimation:
        """Update an existing estimation."""
        update_data = estimation_in.dict(exclude_unset=True)
        
        # Apply updates
        for field, value in update_data.items():
            setattr(estimation, field, value)
        
        # If total cost is updated, recalculate the project's total estimate
        if 'total_cost' in update_data:
            project = db.query(Project).filter(Project.id == estimation.project_id).first()
            if project:
                # If this is the latest estimation, update the project's total
                latest_estimation = db.query(Estimation).filter(
                    Estimation.project_id == project.id
                ).order_by(desc(Estimation.created_at)).first()
                
                if latest_estimation and latest_estimation.id == estimation.id:
                    project.total_estimate = estimation.total_cost
                    db.add(project)
        
        db.add(estimation)
        db.commit()
        db.refresh(estimation)
        return estimation
    
    def delete_estimation(self, db: Session, estimation_id: int) -> None:
        """Delete an estimation."""
        estimation = db.query(Estimation).filter(Estimation.id == estimation_id).first()
        if estimation:
            db.delete(estimation)
            db.commit()
    
    def _estimate_default_materials(self, db: Session, element: Element) -> List[ElementMaterial]:
        """
        Estimate default materials for an element based on its type.
        This is used when no specific materials are associated with an element.
        """
        default_materials = []
        
        # Get base materials from the database
        materials = db.query(Material).all()
        material_map = {material.name: material for material in materials}
        
        # Map element types to default materials and quantities
        if element.element_type == ElementType.WALL:
            # For walls, use area to calculate quantities
            if element.area:
                # Gypsum board (both sides of wall)
                if "Gypsum Board" in material_map:
                    gypsum = ElementMaterial(
                        element_id=element.id,
                        material_id=material_map["Gypsum Board"].id,
                        quantity=element.area * 2,  # Both sides
                        unit=material_map["Gypsum Board"].unit
                    )
                    default_materials.append(gypsum)
                
                # Wood framing
                if "Wood Framing" in material_map:
                    framing = ElementMaterial(
                        element_id=element.id,
                        material_id=material_map["Wood Framing"].id,
                        quantity=element.area * 0.2,  # Estimated framing volume
                        unit=material_map["Wood Framing"].unit
                    )
                    default_materials.append(framing)
                    
                # Insulation
                if "Wall Insulation" in material_map:
                    insulation = ElementMaterial(
                        element_id=element.id,
                        material_id=material_map["Wall Insulation"].id,
                        quantity=element.area,
                        unit=material_map["Wall Insulation"].unit
                    )
                    default_materials.append(insulation)
                    
                # Paint (both sides)
                if "Interior Paint" in material_map:
                    paint = ElementMaterial(
                        element_id=element.id,
                        material_id=material_map["Interior Paint"].id,
                        quantity=element.area * 2,  # Both sides
                        unit=material_map["Interior Paint"].unit
                    )
                    default_materials.append(paint)
                
        elif element.element_type == ElementType.DOOR:
            # For doors, use count
            if "Interior Door" in material_map:
                door = ElementMaterial(
                    element_id=element.id,
                    material_id=material_map["Interior Door"].id,
                    quantity=element.quantity or 1,
                    unit=material_map["Interior Door"].unit
                )
                default_materials.append(door)
                
        elif element.element_type == ElementType.WINDOW:
            # For windows, use area
            if element.area and "Window" in material_map:
                window = ElementMaterial(
                    element_id=element.id,
                    material_id=material_map["Window"].id,
                    quantity=element.area,
                    unit=material_map["Window"].unit
                )
                default_materials.append(window)
        
        return default_materials


estimation_service = EstimationService()
