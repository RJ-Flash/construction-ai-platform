"""
API endpoints for document analysis and quote generation.
"""
import os
import shutil
import tempfile
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import UUID4

from ...schemas.document import (
    DocumentAnalysisResponse,
    DocumentUploadResponse,
    QuoteGenerationRequest,
    QuoteGenerationResponse,
)
from ...services.ai_service import AIService
from ...core.config import settings
from ...core.security import get_current_user
from ...schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a construction document (PDF) for analysis.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Create a unique directory for this user's uploads if it doesn't exist
        user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(user_upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return DocumentUploadResponse(
            success=True,
            filename=file.filename,
            file_path=file_path,
            message="Document uploaded successfully"
        )
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )
    finally:
        file.file.close()

@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    file_path: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a previously uploaded construction document.
    """
    try:
        # Verify the file exists and belongs to the current user
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Ensure the file belongs to the current user (security check)
        user_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
        if not file_path.startswith(user_dir):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this file"
            )
        
        # Initialize the AI service
        ai_service = AIService(api_key=settings.OPENAI_API_KEY)
        
        # Analyze the document
        analysis_result = ai_service.analyze_document(file_path)
        
        if not analysis_result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing document: {analysis_result.get('error', 'Unknown error')}"
            )
        
        return DocumentAnalysisResponse(
            success=True,
            elements=analysis_result.get("elements", []),
            specifications=analysis_result.get("specifications", {}),
            recommendations=analysis_result.get("recommendations", []),
            message="Document analyzed successfully"
        )
    
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing document: {str(e)}"
        )

@router.post("/generate-quote", response_model=QuoteGenerationResponse)
async def generate_quote(
    request: QuoteGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a cost estimate based on analyzed elements.
    """
    try:
        # Initialize the AI service
        ai_service = AIService(api_key=settings.OPENAI_API_KEY)
        
        # Generate the quote
        quote_result = ai_service.generate_quote(
            elements=request.elements,
            region=request.region
        )
        
        if not quote_result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating quote: {quote_result.get('error', 'Unknown error')}"
            )
        
        return QuoteGenerationResponse(
            success=True,
            quote_details=quote_result.get("quote_details", ""),
            estimated_cost_range=_extract_cost_range(quote_result.get("raw_quote", "")),
            message="Quote generated successfully"
        )
    
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"Error generating quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quote: {str(e)}"
        )

def _extract_cost_range(raw_quote: str) -> dict:
    """
    Extract cost range from the raw quote text.
    This is a simplified implementation - in production, we would use 
    more robust parsing.
    """
    # Simple extraction for demonstration purposes
    min_cost = 0
    max_cost = 0
    
    # Look for "Overall project total" or similar
    lines = raw_quote.split("\n")
    for line in lines:
        if "overall" in line.lower() and "total" in line.lower():
            # Try to extract numbers
            import re
            amounts = re.findall(r'\$?[\d,]+(?:\.\d+)?', line)
            if len(amounts) >= 2:
                # Remove non-numeric characters and convert to float
                amounts = [float(amt.replace('$', '').replace(',', '')) for amt in amounts]
                amounts.sort()
                min_cost = amounts[0]
                max_cost = amounts[-1]
            break
    
    return {
        "min": min_cost,
        "max": max_cost,
        "currency": "USD"
    }
