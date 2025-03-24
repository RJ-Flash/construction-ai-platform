"""
MEP API Routes

This module contains the API routes for MEP plugins.
"""
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field

from app.plugins import get_plugin_by_id, get_plugins_by_category
from app.auth.dependencies import get_current_user, User


router = APIRouter(prefix="/mep", tags=["mep"])


class PluginResponse(BaseModel):
    """Response model for a plugin."""
    id: str
    name: str
    description: str
    category: str
    version: str
    price: float


class AnalysisRequest(BaseModel):
    """Request model for plugin analysis."""
    text: str = Field(..., description="The text to analyze")


class AnalysisResponse(BaseModel):
    """Response model for plugin analysis."""
    results: Dict[str, Any] = Field(..., description="The analysis results")


@router.get("/plugins", response_model=List[PluginResponse])
async def list_mep_plugins(current_user: User = Depends(get_current_user)):
    """
    List all available MEP plugins.
    """
    # Get all MEP plugins
    plugins = get_plugins_by_category("mep")
    
    # Create response
    response = []
    for plugin_id, plugin_class in plugins.items():
        plugin = plugin_class()
        response.append(PluginResponse(
            id=plugin.id,
            name=plugin.name,
            description=plugin.description,
            category=plugin.category,
            version=plugin.version,
            price=plugin.price
        ))
    
    return response


@router.post("/analyze/{plugin_id}", response_model=AnalysisResponse)
async def analyze_with_plugin(
    plugin_id: str,
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze text using a specific MEP plugin.
    """
    # Get the plugin
    plugin_class = get_plugin_by_id(plugin_id)
    if not plugin_class:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
    
    # Check if it's an MEP plugin
    plugin = plugin_class()
    if plugin.category != "mep":
        raise HTTPException(status_code=400, detail=f"Plugin '{plugin_id}' is not an MEP plugin")
    
    # Check if the user has purchased this plugin
    # TODO: Implement plugin purchase check
    
    # Analyze the text
    try:
        results = await plugin.analyze(request.text)
        return AnalysisResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
