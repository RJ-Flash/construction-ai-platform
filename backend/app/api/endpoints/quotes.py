"""
Quote generation API endpoints.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from ...core.security import get_current_user
from ...db import models
from ...db.session import get_db
from ...schemas.quote import Quote, QuoteCreate, QuoteUpdate, QuoteItem, QuoteItemCreate
from ...services.ai_service import AIService
from ...core.config import settings

router = APIRouter()


@router.get("/", response_model=List[Quote])
def read_quotes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[UUID4] = Query(None, description="Filter quotes by project"),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve quotes for the current user.
    """
    query = db.query(models.Quote).filter(models.Quote.owner_id == current_user.id)
    
    # Apply project filter if provided
    if project_id:
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
        
        query = query.filter(models.Quote.project_id == project_id)
    
    # Apply pagination
    quotes = query.offset(skip).limit(limit).all()
    
    return quotes


@router.post("/", response_model=Quote)
def create_quote(
    *,
    db: Session = Depends(get_db),
    quote_in: QuoteCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new quote.
    """
    # Verify user has access to the project
    if quote_in.project_id:
        project = db.query(models.Project).filter(
            models.Project.id == quote_in.project_id,
            models.Project.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Create quote
    quote = models.Quote(
        **quote_in.dict(),
        owner_id=current_user.id
    )
    
    db.add(quote)
    db.commit()
    db.refresh(quote)
    
    return quote


@router.get("/{quote_id}", response_model=Quote)
def read_quote(
    *,
    db: Session = Depends(get_db),
    quote_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get quote by ID.
    """
    quote = db.query(models.Quote).filter(
        models.Quote.id == quote_id,
        models.Quote.owner_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    return quote


@router.put("/{quote_id}", response_model=Quote)
def update_quote(
    *,
    db: Session = Depends(get_db),
    quote_id: UUID4,
    quote_in: QuoteUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update quote.
    """
    quote = db.query(models.Quote).filter(
        models.Quote.id == quote_id,
        models.Quote.owner_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    # Update quote
    update_data = quote_in.dict(exclude_unset=True)
    
    # Update fields
    for field in update_data:
        setattr(quote, field, update_data[field])
    
    db.add(quote)
    db.commit()
    db.refresh(quote)
    
    return quote


@router.delete("/{quote_id}", response_model=Quote)
def delete_quote(
    *,
    db: Session = Depends(get_db),
    quote_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete quote.
    """
    quote = db.query(models.Quote).filter(
        models.Quote.id == quote_id,
        models.Quote.owner_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    db.delete(quote)
    db.commit()
    
    return quote


@router.get("/{quote_id}/items", response_model=List[QuoteItem])
def read_quote_items(
    *,
    db: Session = Depends(get_db),
    quote_id: UUID4,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get all items for a quote.
    """
    # Verify user has access to the quote
    quote = db.query(models.Quote).filter(
        models.Quote.id == quote_id,
        models.Quote.owner_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    # Get items
    items = db.query(models.QuoteItem).filter(
        models.QuoteItem.quote_id == quote_id
    ).all()
    
    return items


@router.post("/{quote_id}/items", response_model=QuoteItem)
def create_quote_item(
    *,
    db: Session = Depends(get_db),
    quote_id: UUID4,
    item_in: QuoteItemCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Add an item to a quote.
    """
    # Verify user has access to the quote
    quote = db.query(models.Quote).filter(
        models.Quote.id == quote_id,
        models.Quote.owner_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
    # Create quote item
    item = models.QuoteItem(
        **item_in.dict(),
        quote_id=quote_id
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Update quote totals
    quote.total_min = db.query(models.QuoteItem).filter(
        models.QuoteItem.quote_id == quote_id
    ).with_entities(
        # Sum all cost components for min value
        db.func.sum(
            models.QuoteItem.material_cost_min + 
            models.QuoteItem.labor_cost_min + 
            models.QuoteItem.equipment_cost_min
        )
    ).scalar() or 0
    
    quote.total_max = db.query(models.QuoteItem).filter(
        models.QuoteItem.quote_id == quote_id
    ).with_entities(
        # Sum all cost components for max value
        db.func.sum(
            models.QuoteItem.material_cost_max + 
            models.QuoteItem.labor_cost_max + 
            models.QuoteItem.equipment_cost_max
        )
    ).scalar() or 0
    
    db.add(quote)
    db.commit()
    
    return item


@router.post("/{quote_id}/generate-from-elements", response_model=Quote)
def generate_quote_from_elements(
    *,
    db: Session = Depends(get_db),
    quote_id: UUID4,
    project_id: UUID4 = Body(...),
    region: str = Body(...),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Generate quote items from project elements using AI.
    """
    # Verify user has access to the quote
    quote = db.query(models.Quote).filter(
        models.Quote.id == quote_id,
        models.Quote.owner_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    
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
    
    # Get elements for the project
    elements = db.query(models.Element).filter(
        models.Element.project_id == project_id
    ).all()
    
    if not elements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No elements found for the project"
        )
    
    # Initialize AI service
    ai_service = AIService(api_key=settings.OPENAI_API_KEY)
    
    # Prepare elements for AI service
    element_list = []
    for element in elements:
        element_dict = {
            "type": element.type,
            "dimensions": element.dimensions,
            "materials": element.materials,
            "quantity": element.quantity,
            "notes": element.notes
        }
        element_list.append(element_dict)
    
    # Generate quote using AI
    quote_result = ai_service.generate_quote(
        elements=element_list,
        region=region
    )
    
    if not quote_result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quote: {quote_result.get('error', 'Unknown error')}"
        )
    
    # Extract cost ranges
    cost_range = quote_result.get("quote_details", {}).get("estimated_cost_range", {})
    min_cost = cost_range.get("min", 0)
    max_cost = cost_range.get("max", 0)
    
    # Update quote
    quote.total_min = min_cost
    quote.total_max = max_cost
    quote.region = region
    quote.project_id = project_id
    quote.notes = quote_result.get("quote_details", "")
    
    db.add(quote)
    db.commit()
    db.refresh(quote)
    
    return quote
