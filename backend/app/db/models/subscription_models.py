from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text, DateTime, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from ..base_class import Base

# Subscription plan enum
class PlanType(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    ESSENTIAL = "essential"
    PROFESSIONAL = "professional"
    ADVANCED = "advanced"
    ULTIMATE = "ultimate"

# Organization model
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    subscription = relationship("Subscription", back_populates="organization", uselist=False)
    plugin_licenses = relationship("PluginLicense", back_populates="organization")
    usage_records = relationship("UsageRecord", back_populates="organization")

# Subscription model
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    plan_type = Column(Enum(PlanType), default=PlanType.FREE)
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    max_users = Column(Integer, default=1)
    max_documents = Column(Integer, default=1)  # Per month
    documents_used = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    billing_cycle = Column(String, default="monthly")  # monthly or annual
    payment_method = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    
# Plugin License model
class PluginLicense(Base):
    __tablename__ = "plugin_licenses"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    plugin_id = Column(String, index=True)
    plugin_name = Column(String)
    is_active = Column(Boolean, default=True)
    license_key = Column(String, unique=True)
    price = Column(Float, default=0.0)
    billing_cycle = Column(String)  # one-time, monthly, annual
    purchase_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="plugin_licenses")

# Usage record model
class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String, index=True)  # document_upload, document_analysis, plugin_usage
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    plugin_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="usage_records")
    user = relationship("User", back_populates="usage_records")
    document = relationship("Document", back_populates="usage_records")
