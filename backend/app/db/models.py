"""
Database Models

This module contains SQLAlchemy models for the database.
"""
import datetime
import uuid
from typing import Optional, List, Dict, Any
import json

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.config import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    date_joined = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    purchased_plugins = relationship("UserPlugin", back_populates="user", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Subscription(Base):
    """Subscription model."""
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    tier = Column(String(50), nullable=False)  # "free", "professional", "enterprise"
    price = Column(Float, nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    payment_id = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription {self.tier} for {self.user_id}>"


class UserPlugin(Base):
    """User-Plugin relationship model."""
    __tablename__ = "user_plugins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plugin_id = Column(String(255), nullable=False)
    purchase_date = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    payment_id = Column(String(255), nullable=True)
    
    # Unique constraint to prevent duplicate purchases
    __table_args__ = (UniqueConstraint("user_id", "plugin_id", name="_user_plugin_uc"),)
    
    # Relationships
    user = relationship("User", back_populates="purchased_plugins")
    
    def __repr__(self):
        return f"<UserPlugin {self.plugin_id} for {self.user_id}>"


class AnalysisResult(Base):
    """Analysis result model."""
    __tablename__ = "analysis_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plugin_id = Column(String(255), nullable=False)
    project_id = Column(String(36), nullable=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    input_text = Column(Text, nullable=False)
    _results_json = Column("results_json", Text, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analysis_results")
    
    @hybrid_property
    def results(self) -> Dict[str, Any]:
        """Get the results as a Python dictionary."""
        return json.loads(self._results_json)
    
    @results.setter
    def results(self, value: Dict[str, Any]):
        """Set the results from a Python dictionary."""
        self._results_json = json.dumps(value)
    
    def __repr__(self):
        return f"<AnalysisResult {self.name} by {self.plugin_id}>"


class Project(Base):
    """Project model."""
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Project {self.name}>"


class Document(Base):
    """Document model for storing construction documents."""
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)  # "specification", "drawing", "contract", etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Document {self.name}>"


class BIMIntegration(Base):
    """BIM Integration model for storing BIM integration details."""
    __tablename__ = "bim_integrations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # "revit", "archicad", "bentley", etc.
    api_key = Column(String(512), nullable=True)
    connection_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<BIMIntegration {self.name} for {self.platform}>"
