"""
Schema definitions for document analysis and quote generation.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ConstructionElement(BaseModel):
    """A construction element extracted from a document."""
    type: str = Field(..., description="Type of construction element")
    dimensions: Optional[str] = Field(None, description="Dimensions of the element")
    materials: Optional[str] = Field(None, description="Materials specified for the element")
    quantity: Optional[str] = Field(None, description="Quantity of elements")
    notes: Optional[str] = Field(None, description="Special requirements or notes")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "wall",
                "dimensions": "10' x 8'",
                "materials": "concrete blocks, 8\" thick",
                "quantity": "4",
                "notes": "Requires waterproofing"
            }
        }


class DocumentUploadResponse(BaseModel):
    """Response for document upload endpoint."""
    success: bool = Field(..., description="Whether the upload was successful")
    filename: str = Field(..., description="Name of the uploaded file")
    file_path: str = Field(..., description="Path where the file was saved")
    message: str = Field(..., description="Success/error message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "filename": "building_plans.pdf",
                "file_path": "/uploads/123/building_plans.pdf",
                "message": "Document uploaded successfully"
            }
        }


class DocumentAnalysisResponse(BaseModel):
    """Response for document analysis endpoint."""
    success: bool = Field(..., description="Whether the analysis was successful")
    elements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted construction elements"
    )
    specifications: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted project specifications"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="AI-generated recommendations"
    )
    message: str = Field(..., description="Success/error message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "elements": [
                    {
                        "type": "foundation",
                        "dimensions": "40' x 30'",
                        "materials": "reinforced concrete",
                        "quantity": "1"
                    },
                    {
                        "type": "wall",
                        "dimensions": "10' x 8'",
                        "materials": "concrete blocks, 8\" thick",
                        "quantity": "4"
                    }
                ],
                "specifications": {
                    "building_codes": [
                        "IBC 2018",
                        "ASHRAE 90.1-2019"
                    ],
                    "quality_requirements": [
                        "All concrete to have minimum 3,000 PSI strength",
                        "Rebar to be ASTM A615 Grade 60"
                    ]
                },
                "recommendations": [
                    "Consider bulk purchasing of wall materials to reduce costs",
                    "Verify all materials meet or exceed specified quality standards"
                ],
                "message": "Document analyzed successfully"
            }
        }


class CostRange(BaseModel):
    """Cost range for a quote."""
    min: float = Field(..., description="Minimum estimated cost")
    max: float = Field(..., description="Maximum estimated cost")
    currency: str = Field("USD", description="Currency code")
    
    class Config:
        schema_extra = {
            "example": {
                "min": 150000.0,
                "max": 180000.0,
                "currency": "USD"
            }
        }


class QuoteGenerationRequest(BaseModel):
    """Request for quote generation endpoint."""
    elements: List[Dict[str, Any]] = Field(
        ..., 
        description="Construction elements to include in the quote"
    )
    region: str = Field(
        ..., 
        description="Geographic region for cost adjustment"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional client preferences for materials, etc."
    )
    
    class Config:
        schema_extra = {
            "example": {
                "elements": [
                    {
                        "type": "foundation",
                        "dimensions": "40' x 30'",
                        "materials": "reinforced concrete",
                        "quantity": "1"
                    },
                    {
                        "type": "wall",
                        "dimensions": "10' x 8'",
                        "materials": "concrete blocks, 8\" thick",
                        "quantity": "4"
                    }
                ],
                "region": "Northeast US",
                "preferences": {
                    "sustainable_materials": True,
                    "premium_finishes": False
                }
            }
        }


class QuoteGenerationResponse(BaseModel):
    """Response for quote generation endpoint."""
    success: bool = Field(..., description="Whether the quote generation was successful")
    quote_details: str = Field(
        ..., 
        description="Detailed quote breakdown"
    )
    estimated_cost_range: CostRange = Field(
        ...,
        description="Estimated cost range for the project"
    )
    message: str = Field(..., description="Success/error message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "quote_details": "# Project Cost Estimate\n\n## Foundation\n- Materials: $45,000-$50,000\n- Labor: $20,000-$25,000\n...",
                "estimated_cost_range": {
                    "min": 150000.0,
                    "max": 180000.0,
                    "currency": "USD"
                },
                "message": "Quote generated successfully"
            }
        }
