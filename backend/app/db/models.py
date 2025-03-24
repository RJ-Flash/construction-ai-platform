"""
SQLAlchemy database models.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base_class import Base


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    company_name = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    documents = relationship("Document", back_populates="owner")
    quotes = relationship("Quote", back_populates="owner")


class Project(Base):
    """Construction project model."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    location = Column(String, index=True)
    client_name = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String, index=True, default="planning")
    
    # Metadata fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project")
    quotes = relationship("Quote", back_populates="project")
    elements = relationship("Element", back_populates="project")


class Document(Base):
    """Construction document model (blueprints, plans, etc.)."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    description = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Document analysis status
    is_analyzed = Column(Boolean, default=False)
    analysis_date = Column(DateTime)
    analysis_status = Column(String, default="pending")
    analysis_message = Column(Text)
    
    # Foreign keys
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    project = relationship("Project", back_populates="documents")
    elements = relationship("Element", back_populates="source_document")


class Element(Base):
    """Construction element extracted from documents."""
    __tablename__ = "elements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, index=True, nullable=False)
    dimensions = Column(String)
    materials = Column(String)
    quantity = Column(String)
    notes = Column(Text)
    
    # Additional specifications as JSON
    specifications = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    source_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    
    # Relationships
    project = relationship("Project", back_populates="elements")
    source_document = relationship("Document", back_populates="elements")
    quote_items = relationship("QuoteItem", back_populates="element")


class Quote(Base):
    """Construction quote/estimate model."""
    __tablename__ = "quotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(Text)
    region = Column(String, index=True)
    version = Column(String, default="1.0")
    status = Column(String, default="draft")
    
    # Financial summary
    total_min = Column(Float)
    total_max = Column(Float)
    currency = Column(String, default="USD")
    
    # Additional data
    notes = Column(Text)
    preferences = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    
    # Relationships
    owner = relationship("User", back_populates="quotes")
    project = relationship("Project", back_populates="quotes")
    items = relationship("QuoteItem", back_populates="quote")


class QuoteItem(Base):
    """Individual line item in a quote."""
    __tablename__ = "quote_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String, nullable=False)
    category = Column(String, index=True)
    
    # Cost breakdown
    material_cost_min = Column(Float)
    material_cost_max = Column(Float)
    labor_cost_min = Column(Float)
    labor_cost_max = Column(Float)
    equipment_cost_min = Column(Float)
    equipment_cost_max = Column(Float)
    
    # Time estimates
    time_estimate_min = Column(Float)  # Hours
    time_estimate_max = Column(Float)  # Hours
    
    # Additional data
    notes = Column(Text)
    specifications = Column(JSON)
    
    # Foreign keys
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id"))
    element_id = Column(UUID(as_uuid=True), ForeignKey("elements.id"))
    
    # Relationships
    quote = relationship("Quote", back_populates="items")
    element = relationship("Element", back_populates="quote_items")
