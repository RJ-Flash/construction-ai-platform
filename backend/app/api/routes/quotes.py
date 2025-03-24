from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ...db.database import get_db
from ...db.models import Quote, QuoteItem, QuoteActivity, Project, Element, Client, User, QuoteStatus
from ...schemas import quotes as schemas
from ...core.security import get_current_active_user
from ...services.pdf_service import PDFService

router = APIRouter()

@router.get("/", response_model=List[schemas.Quote])
def read_quotes(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve quotes with optional filtering by project, client, or status.
    """
    query = db.query(Quote)
    
    # Filter by project if specified
    if project_id:
        # Verify project exists and user has access
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        if project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")
            
        query = query.filter(Quote.project_id == project_id)
    else:
        # If no project specified, show quotes from projects user has access to
        query = query.join(Project).filter(
            (Project.owner_id == current_user.id) | 
            (Project.users.any(id=current_user.id))
        )
    
    # Filter by client if specified
    if client_id:
        query = query.filter(Quote.client_id == client_id)
    
    # Filter by status if specified
    if status:
        try:
            quote_status = QuoteStatus(status)
            query = query.filter(Quote.status == quote_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status value: {status}")
    
    quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
    return quotes

@router.get("/{quote_id}", response_model=schemas.QuoteWithItems)
def read_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific quote by ID with all items.
    """
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to access this quote")
    
    return quote

@router.post("/", response_model=schemas.Quote)
def create_quote(
    quote: schemas.QuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new quote.
    """
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == quote.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # If client_id provided, verify it exists
    if quote.client_id:
        client = db.query(Client).filter(Client.id == quote.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
    
    # Calculate default expiry date if not provided (30 days from now)
    if not quote.expiry_date:
        quote.expiry_date = datetime.utcnow() + timedelta(days=30)
    
    # Create quote object
    db_quote = Quote(
        title=quote.title,
        status=QuoteStatus.DRAFT,
        client_name=quote.client_name,
        client_email=quote.client_email,
        client_phone=quote.client_phone,
        notes=quote.notes,
        tax_rate=quote.tax_rate,
        discount_percentage=quote.discount_percentage,
        project_id=quote.project_id,
        client_id=quote.client_id,
        created_by=current_user.id,
        expiry_date=quote.expiry_date,
        organization_id=current_user.organization_id
    )
    
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    
    # Add initial activity record
    activity = QuoteActivity(
        action="created",
        notes="Quote created",
        user_id=current_user.id,
        quote_id=db_quote.id
    )
    
    db.add(activity)
    db.commit()
    
    return db_quote

@router.put("/{quote_id}", response_model=schemas.Quote)
def update_quote(
    quote_id: int,
    quote: schemas.QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to update this quote")
    
    # Update quote with new data
    update_data = quote.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_quote, key, value)
    
    db.commit()
    db.refresh(db_quote)
    
    # Add activity record for update
    activity = QuoteActivity(
        action="updated",
        notes="Quote details updated",
        user_id=current_user.id,
        quote_id=db_quote.id
    )
    
    db.add(activity)
    db.commit()
    
    return db_quote

@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this quote")
    
    db.delete(db_quote)
    db.commit()
    
    return None

@router.post("/{quote_id}/items", response_model=schemas.QuoteItem)
def add_quote_item(
    quote_id: int,
    item: schemas.QuoteItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add an item to a quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to modify this quote")
    
    # If element_id provided, verify it exists and user has access
    if item.element_id:
        element = db.query(Element).filter(Element.id == item.element_id).first()
        if not element:
            raise HTTPException(status_code=404, detail="Element not found")
        
        if element.project_id and element.project_id != db_quote.project_id:
            raise HTTPException(status_code=400, detail="Element does not belong to the same project as the quote")
    
    # Create the quote item
    total_price = item.unit_price * item.quantity
    
    db_item = QuoteItem(
        description=item.description,
        details=item.details,
        quantity=item.quantity,
        unit_price=item.unit_price,
        total_price=total_price,
        quote_id=quote_id,
        element_id=item.element_id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Update quote totals
    update_quote_totals(db, db_quote)
    
    # Add activity record
    activity = QuoteActivity(
        action="item_added",
        notes=f"Added item: {item.description}",
        user_id=current_user.id,
        quote_id=quote_id
    )
    
    db.add(activity)
    db.commit()
    
    return db_item

@router.put("/items/{item_id}", response_model=schemas.QuoteItem)
def update_quote_item(
    item_id: int,
    item: schemas.QuoteItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a quote item.
    """
    db_item = db.query(QuoteItem).filter(QuoteItem.id == item_id).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Quote item not found")
    
    # Check if user has access to modify this quote
    db_quote = db.query(Quote).filter(Quote.id == db_item.quote_id).first()
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to modify this quote")
    
    # Update item with new data
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    # Recalculate total price if quantity or unit price was updated
    if 'quantity' in update_data or 'unit_price' in update_data:
        db_item.total_price = db_item.unit_price * db_item.quantity
    
    db.commit()
    db.refresh(db_item)
    
    # Update quote totals
    update_quote_totals(db, db_quote)
    
    # Add activity record
    activity = QuoteActivity(
        action="item_updated",
        notes=f"Updated item: {db_item.description}",
        user_id=current_user.id,
        quote_id=db_item.quote_id
    )
    
    db.add(activity)
    db.commit()
    
    return db_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a quote item.
    """
    db_item = db.query(QuoteItem).filter(QuoteItem.id == item_id).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Quote item not found")
    
    # Check if user has access to modify this quote
    db_quote = db.query(Quote).filter(Quote.id == db_item.quote_id).first()
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to modify this quote")
    
    # Save description for activity log
    description = db_item.description
    
    # Delete the item
    db.delete(db_item)
    db.commit()
    
    # Update quote totals
    update_quote_totals(db, db_quote)
    
    # Add activity record
    activity = QuoteActivity(
        action="item_removed",
        notes=f"Removed item: {description}",
        user_id=current_user.id,
        quote_id=db_quote.id
    )
    
    db.add(activity)
    db.commit()
    
    return None

@router.post("/{quote_id}/elements", response_model=List[schemas.QuoteItem])
def add_elements_to_quote(
    quote_id: int,
    element_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add multiple elements to a quote as quote items.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to modify this quote")
    
    # Get the elements
    elements = db.query(Element).filter(Element.id.in_(element_ids)).all()
    
    # Check if all elements exist
    if len(elements) != len(element_ids):
        raise HTTPException(status_code=404, detail="One or more elements not found")
    
    # Check if all elements belong to the same project as the quote
    for element in elements:
        if element.project_id and element.project_id != db_quote.project_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Element {element.id} does not belong to the same project as the quote"
            )
    
    # Create quote items from elements
    created_items = []
    for element in elements:
        # Calculate price (use element's estimated price if available)
        unit_price = element.estimated_price or 0
        quantity = element.quantity or 1
        total_price = unit_price * quantity
        
        # Create quote item
        db_item = QuoteItem(
            description=f"{element.type} - {element.materials or 'No material'} - {element.dimensions or 'No dimensions'}",
            details=element.notes,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            quote_id=quote_id,
            element_id=element.id
        )
        
        db.add(db_item)
        created_items.append(db_item)
    
    db.commit()
    
    # Refresh items to get their IDs
    for item in created_items:
        db.refresh(item)
    
    # Update quote totals
    update_quote_totals(db, db_quote)
    
    # Add activity record
    activity = QuoteActivity(
        action="elements_added",
        notes=f"Added {len(created_items)} elements to quote",
        user_id=current_user.id,
        quote_id=quote_id
    )
    
    db.add(activity)
    db.commit()
    
    return created_items

@router.post("/{quote_id}/status", response_model=schemas.Quote)
def update_quote_status(
    quote_id: int,
    status_update: schemas.QuoteStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the status of a quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to modify this quote")
    
    # Validate status transition
    try:
        new_status = QuoteStatus(status_update.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status value: {status_update.status}")
    
    # Update quote status
    db_quote.status = new_status
    db.commit()
    db.refresh(db_quote)
    
    # Add activity record
    activity = QuoteActivity(
        action="status_changed",
        notes=f"Status changed to: {new_status}",
        user_id=current_user.id,
        quote_id=quote_id
    )
    
    db.add(activity)
    db.commit()
    
    return db_quote

@router.get("/{quote_id}/activities", response_model=List[schemas.QuoteActivity])
def get_quote_activities(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the activity history for a quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to access this quote")
    
    activities = db.query(QuoteActivity).filter(QuoteActivity.quote_id == quote_id).order_by(QuoteActivity.timestamp.desc()).all()
    return activities

@router.post("/{quote_id}/generate-pdf", response_model=schemas.Quote)
def generate_quote_pdf(
    quote_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a PDF version of the quote.
    """
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to access this quote")
    
    # Add PDF generation task to background tasks
    background_tasks.add_task(generate_quote_pdf_task, db_quote.id, db, current_user.id)
    
    # Add activity record
    activity = QuoteActivity(
        action="pdf_generated",
        notes="PDF generation started",
        user_id=current_user.id,
        quote_id=quote_id
    )
    
    db.add(activity)
    db.commit()
    
    return db_quote

@router.get("/{quote_id}/download-pdf")
def download_quote_pdf(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download the PDF version of a quote.
    """
    # This would typically return a FileResponse, but that implementation
    # depends on the PDF generation service and file storage
    # For now, we'll just check access and return a placeholder response
    
    db_quote = db.query(Quote).filter(Quote.id == quote_id).first()
    
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Check if user has access to the project this quote belongs to
    project = db.query(Project).filter(Project.id == db_quote.project_id).first()
    if project and project.owner_id != current_user.id and current_user.id not in [u.id for u in project.users]:
        raise HTTPException(status_code=403, detail="Not authorized to access this quote")
    
    # Return placeholder response
    return {
        "status": "success",
        "message": "PDF download functionality will be implemented with the PDF generation service."
    }

# Helper functions
def update_quote_totals(db: Session, quote: Quote):
    """
    Update the total amounts on a quote based on its items.
    """
    # Get all items for this quote
    items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote.id).all()
    
    # Calculate subtotal
    subtotal = sum(item.total_price for item in items)
    
    # Calculate discount amount
    discount_amount = subtotal * (quote.discount_percentage / 100) if quote.discount_percentage else 0
    
    # Calculate tax amount on the discounted total
    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * (quote.tax_rate / 100) if quote.tax_rate else 0
    
    # Calculate total amount
    total_amount = taxable_amount + tax_amount
    
    # Update quote with calculated values
    quote.subtotal_amount = subtotal
    quote.discount_amount = discount_amount
    quote.tax_amount = tax_amount
    quote.total_amount = total_amount
    
    db.commit()

async def generate_quote_pdf_task(quote_id: int, db: Session, user_id: int):
    """
    Background task to generate a PDF for a quote.
    """
    # This would typically use the PDFService, but that implementation
    # depends on the PDF generation service
    # For now, we'll just add an activity record
    
    # Add activity record when complete
    activity = QuoteActivity(
        action="pdf_generated",
        notes="PDF generation completed",
        user_id=user_id,
        quote_id=quote_id
    )
    
    db.add(activity)
    db.commit()
