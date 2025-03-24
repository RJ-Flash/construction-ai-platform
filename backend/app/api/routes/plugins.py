from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...schemas import User as UserSchema
from ...core.auth import get_current_active_user
from ...plugins import get_available_plugins, get_plugin_by_id, PluginManager
from ...plugins.base import AnalysisPlugin

router = APIRouter()

# Plugin manager instance
plugin_manager = PluginManager()

# Load all available plugins
for plugin_class in [get_plugin_by_id(plugin_info["id"]) for plugin_info in get_available_plugins()]:
    if plugin_class:
        plugin_manager.register_plugin(plugin_class())
        # Enable plugin by default for development
        plugin_manager.enable_plugin(plugin_class.id)

@router.get("/", response_model=List[Dict[str, Any]])
async def list_plugins(
    category: Optional[str] = None,
    enabled_only: bool = False,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    List all available plugins, optionally filtered by category.
    """
    if enabled_only:
        plugins = plugin_manager.list_enabled_plugins()
    else:
        plugins = plugin_manager.list_plugins()
    
    # Filter by category if specified
    if category:
        plugins = [plugin for plugin in plugins if plugin.get("category") == category]
    
    return plugins

@router.get("/{plugin_id}", response_model=Dict[str, Any])
async def get_plugin_details(
    plugin_id: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get details of a specific plugin.
    """
    plugin = plugin_manager.get_plugin(plugin_id)
    
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin with ID '{plugin_id}' not found"
        )
    
    return {
        **plugin.metadata,
        "enabled": plugin_id in plugin_manager.enabled_plugins
    }

@router.post("/{plugin_id}/enable", response_model=Dict[str, Any])
async def enable_plugin(
    plugin_id: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Enable a plugin.
    """
    try:
        plugin_manager.enable_plugin(plugin_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    plugin = plugin_manager.get_plugin(plugin_id)
    
    return {
        **plugin.metadata,
        "enabled": True
    }

@router.post("/{plugin_id}/disable", response_model=Dict[str, Any])
async def disable_plugin(
    plugin_id: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Disable a plugin.
    """
    try:
        plugin_manager.disable_plugin(plugin_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    plugin = plugin_manager.get_plugin(plugin_id)
    
    return {
        **plugin.metadata,
        "enabled": False
    }

@router.post("/{plugin_id}/analyze", response_model=Dict[str, Any])
async def analyze_with_plugin(
    plugin_id: str,
    text: str = Body(..., embed=True),
    context: Optional[Dict[str, Any]] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Analyze text using a specific plugin.
    """
    try:
        results = await plugin_manager.run_analysis(text, plugin_id, context)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return results

@router.post("/analyze_all", response_model=Dict[str, Dict[str, Any]])
async def analyze_with_all_plugins(
    text: str = Body(..., embed=True),
    context: Optional[Dict[str, Any]] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Analyze text using all enabled plugins.
    """
    results = await plugin_manager.run_all_enabled_plugins(text, context)
    return results