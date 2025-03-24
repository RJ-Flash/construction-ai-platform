from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.db.models.plugin import PluginCategory, PluginStatus

class PluginBase(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    author: Optional[str] = None
    license_type: Optional[str] = None
    is_free: Optional[bool] = None
    price: Optional[float] = None
    icon_url: Optional[str] = None

    @validator("category")
    def validate_category(cls, v):
        if v is not None and v not in [cat.value for cat in PluginCategory]:
            raise ValueError(f"Invalid category. Must be one of: {', '.join([cat.value for cat in PluginCategory])}")
        return v

    @validator("status")
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in PluginStatus]:
            raise ValueError(f"Invalid status. Must be one of: {', '.join([status.value for status in PluginStatus])}")
        return v

class PluginCreate(PluginBase):
    name: str
    version: str
    category: str
    entry_point: str
    package_path: str
    author: str
    config: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None
    is_system: Optional[bool] = False

class PluginUpdate(PluginBase):
    entry_point: Optional[str] = None
    package_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None

class PluginInDBBase(PluginBase):
    id: int
    entry_point: str
    package_path: str
    config: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None
    is_system: bool
    installed_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class PluginResponse(PluginInDBBase):
    pass
