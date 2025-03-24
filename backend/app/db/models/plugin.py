from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base

class PluginCategory(str, enum.Enum):
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    STRUCTURAL = "structural"
    FINISHES = "finishes"
    SITE_WORK = "site_work"
    GENERAL = "general"
    UTILITY = "utility"

class PluginStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"

class Plugin(Base):
    __tablename__ = "plugins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(PluginCategory), nullable=False)
    status = Column(Enum(PluginStatus), default=PluginStatus.ACTIVE)
    
    # Plugin details
    entry_point = Column(String(255), nullable=False)  # Main entry point for the plugin
    package_path = Column(String(512), nullable=False)  # Path to the plugin package
    config = Column(JSON, nullable=True)  # Plugin configuration
    requirements = Column(JSON, nullable=True)  # Plugin dependencies
    icon_url = Column(String(255), nullable=True)  # URL to the plugin icon
    
    # Licensing
    author = Column(String(255), nullable=False)
    license_type = Column(String(50), nullable=True)
    is_free = Column(Boolean, default=False)
    price = Column(Float, nullable=True)
    
    # User access control
    is_system = Column(Boolean, default=False)  # System plugins cannot be deleted
    
    # Installation metadata
    installed_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Plugin {self.id}: {self.name} v{self.version}>"
