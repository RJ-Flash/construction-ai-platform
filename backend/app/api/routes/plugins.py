from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.db.models.user import User
from app.schemas.plugin import PluginCreate, PluginResponse, PluginUpdate
from app.services.plugin import plugin_service

router = APIRouter()

@router.get("/", response_model=List[PluginResponse])
def get_plugins(
    *,
    db: Session = Depends(deps.get_db),
    category: Optional[str] = Query(None, description="Filter by plugin category"),
    status: Optional[str] = Query(None, description="Filter by plugin status"),
    is_free: Optional[bool] = Query(None, description="Filter by free/paid plugins"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get list of available plugins.
    """
    return plugin_service.get_plugins(
        db=db, 
        category=category, 
        status=status, 
        is_free=is_free,
        skip=skip, 
        limit=limit
    )

@router.get("/{plugin_id}", response_model=PluginResponse)
def get_plugin(
    *,
    db: Session = Depends(deps.get_db),
    plugin_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get plugin by ID.
    """
    plugin = plugin_service.get_plugin(db=db, plugin_id=plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )
    return plugin

@router.post("/", response_model=PluginResponse, status_code=status.HTTP_201_CREATED)
def create_plugin(
    *,
    db: Session = Depends(deps.get_db),
    plugin_in: PluginCreate,
    current_user: User = Depends(deps.get_current_superuser)
):
    """
    Create a new plugin (admin only).
    """
    return plugin_service.create_plugin(db=db, plugin_in=plugin_in)

@router.post("/upload", response_model=PluginResponse, status_code=status.HTTP_201_CREATED)
async def upload_plugin(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_superuser)
):
    """
    Upload a plugin package (admin only).
    """
    return await plugin_service.upload_plugin(db=db, file=file)

@router.put("/{plugin_id}", response_model=PluginResponse)
def update_plugin(
    *,
    db: Session = Depends(deps.get_db),
    plugin_id: int,
    plugin_in: PluginUpdate,
    current_user: User = Depends(deps.get_current_superuser)
):
    """
    Update plugin information (admin only).
    """
    plugin = plugin_service.get_plugin(db=db, plugin_id=plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )
    
    if plugin.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System plugins cannot be modified"
        )
    
    plugin = plugin_service.update_plugin(db=db, plugin=plugin, plugin_in=plugin_in)
    return plugin

@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plugin(
    *,
    db: Session = Depends(deps.get_db),
    plugin_id: int,
    current_user: User = Depends(deps.get_current_superuser)
):
    """
    Delete a plugin (admin only).
    """
    plugin = plugin_service.get_plugin(db=db, plugin_id=plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )
    
    if plugin.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System plugins cannot be deleted"
        )
    
    plugin_service.delete_plugin(db=db, plugin_id=plugin_id)
    return None

@router.post("/{plugin_id}/install", response_model=PluginResponse)
def install_plugin(
    *,
    db: Session = Depends(deps.get_db),
    plugin_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Install a plugin for use.
    """
    plugin = plugin_service.get_plugin(db=db, plugin_id=plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )
    
    if plugin.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active plugins can be installed"
        )
    
    return plugin_service.install_plugin(db=db, plugin=plugin, user_id=current_user.id)

@router.post("/{plugin_id}/uninstall", response_model=PluginResponse)
def uninstall_plugin(
    *,
    db: Session = Depends(deps.get_db),
    plugin_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Uninstall a plugin.
    """
    plugin = plugin_service.get_plugin(db=db, plugin_id=plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )
    
    return plugin_service.uninstall_plugin(db=db, plugin=plugin, user_id=current_user.id)
