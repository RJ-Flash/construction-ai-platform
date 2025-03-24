from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text, DateTime, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from ..database import Base

# Subscription plan enum
class PlanType(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    ESSENTIAL = "essential"
    PROFESSIONAL = "professional"
    ADVANCED = "advanced"
    ULTIMATE = "ultimate"

# Association table for organization plugins
organization_plugins = Table(
    "organization_plugins",
    Base.metadata,
    Column("organization_id", Integer, ForeignKey("organizations.id"), primary_key=True),
    Column("plugin_id", String, primary_key=True),
)

# Organization model
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    subscription = relationship("Subscription", back_populates="organization", uselist=False)
    plugins = relationship("PluginLicense", back_populates="organization")

# Subscription model
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), unique=True)
    plan_type = Column(Enum(PlanType), default=PlanType.FREE)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    max_users = Column(Integer, default=1)
    max_documents = Column(Integer, default=1)
    documents_used = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    billing_cycle = Column(String, default="monthly")  # monthly or annual
    payment_method = Column(String)
    payment_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscription")

# Plugin license model
class PluginLicense(Base):
    __tablename__ = "plugin_licenses"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    plugin_id = Column(String, index=True)
    plugin_name = Column(String)
    license_key = Column(String, unique=True)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    price = Column(Float, default=0.0)
    billing_cycle = Column(String, default="one-time")  # one-time, monthly, annual
    payment_id = Column(String)
    
    # Relationships
    organization = relationship("Organization", back_populates="plugins")

# Usage tracking model
class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    plugin_id = Column(String, nullable=True)
    action_type = Column(String)  # document_upload, document_analysis, plugin_usage
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    document = relationship("Document", back_populates="usage_records")

# Add relationship to User model
from ..models import User
User.organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
User.organization = relationship("Organization", back_populates="users")

# Add relationship to Project model
from ..models import Project
Project.organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
Project.organization = relationship("Organization", back_populates="projects")

# Add relationship to Document model
from ..models import Document
Document.usage_records = relationship("UsageRecord", back_populates="document")