from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text, DateTime, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from .database import Base

# Association tables
project_users = Table(
    "project_users",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

# Enums
class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", secondary=project_users, back_populates="users")
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")

# Project model
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    users = relationship("User", secondary=project_users, back_populates="projects")
    documents = relationship("Document", back_populates="project")
    elements = relationship("Element", back_populates="project")
    quotes = relationship("Quote", back_populates="project")

# Client model
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Relationships
    project = relationship("Project")
    quotes = relationship("Quote", back_populates="client")

# Document model
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    is_analyzed = Column(Boolean, default=False)
    analysis_status = Column(String, default="not_analyzed")
    analysis_date = Column(DateTime, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", back_populates="documents")
    elements = relationship("Element", back_populates="document")
    specifications = relationship("DocumentSpecification", back_populates="document")

# DocumentSpecification model
class DocumentSpecification(Base):
    __tablename__ = "document_specifications"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    key = Column(String, index=True)
    value = Column(Text)
    document_id = Column(Integer, ForeignKey("documents.id"))

    # Relationships
    document = relationship("Document", back_populates="specifications")

# Element model
class Element(Base):
    __tablename__ = "elements"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    materials = Column(String, nullable=True)
    dimensions = Column(String, nullable=True)
    quantity = Column(Float, default=1.0)
    estimated_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="elements")
    project = relationship("Project", back_populates="elements")
    quote_items = relationship("QuoteItem", back_populates="element")

# Quote model
class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    client_name = Column(String, nullable=True)
    client_email = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    tax_rate = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)
    subtotal_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", back_populates="quotes")
    client = relationship("Client", back_populates="quotes")
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")
    activities = relationship("QuoteActivity", back_populates="quote", cascade="all, delete-orphan")

# QuoteItem model
class QuoteItem(Base):
    __tablename__ = "quote_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    details = Column(Text, nullable=True)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    element_id = Column(Integer, ForeignKey("elements.id"), nullable=True)

    # Relationships
    quote = relationship("Quote", back_populates="items")
    element = relationship("Element", back_populates="quote_items")

# QuoteActivity model
class QuoteActivity(Base):
    __tablename__ = "quote_activities"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"))

    # Relationships
    quote = relationship("Quote", back_populates="activities")
    user = relationship("User")