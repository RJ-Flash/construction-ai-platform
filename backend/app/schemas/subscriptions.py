from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Plan type enum
class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    ESSENTIAL = "essential"
    PROFESSIONAL = "professional"
    ADVANCED = "advanced"
    ULTIMATE = "ultimate"

# Organization schemas
class OrganizationBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class OrganizationInDBBase(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Organization(OrganizationInDBBase):
    pass

# Subscription schemas
class SubscriptionBase(BaseModel):
    plan_type: PlanType = PlanType.FREE
    is_active: bool = True
    is_trial: bool = False
    max_users: int = 1
    max_documents: int = 1
    documents_used: int = 0
    price: float = 0.0
    billing_cycle: str = "monthly"
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None

class SubscriptionCreate(SubscriptionBase):
    organization_id: int
    start_date: datetime = datetime.utcnow()
    end_date: Optional[datetime] = None

class SubscriptionUpdate(BaseModel):
    plan_type: Optional[PlanType] = None
    is_active: Optional[bool] = None
    is_trial: Optional[bool] = None
    max_users: Optional[int] = None
    max_documents: Optional[int] = None
    documents_used: Optional[int] = None
    price: Optional[float] = None
    billing_cycle: Optional[str] = None
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    end_date: Optional[datetime] = None

class SubscriptionInDBBase(SubscriptionBase):
    id: int
    organization_id: int
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Subscription(SubscriptionInDBBase):
    pass

# Plugin license schemas
class PluginLicenseBase(BaseModel):
    plugin_id: str
    plugin_name: str
    license_key: str
    is_active: bool = True
    price: float = 0.0
    billing_cycle: str = "one-time"
    payment_id: Optional[str] = None

class PluginLicenseCreate(PluginLicenseBase):
    organization_id: int
    purchase_date: datetime = datetime.utcnow()
    expiry_date: Optional[datetime] = None

class PluginLicenseUpdate(BaseModel):
    is_active: Optional[bool] = None
    expiry_date: Optional[datetime] = None
    price: Optional[float] = None
    billing_cycle: Optional[str] = None
    payment_id: Optional[str] = None

class PluginLicenseInDBBase(PluginLicenseBase):
    id: int
    organization_id: int
    purchase_date: datetime
    expiry_date: Optional[datetime]

    class Config:
        orm_mode = True

class PluginLicense(PluginLicenseInDBBase):
    pass

# Usage record schemas
class UsageRecordBase(BaseModel):
    organization_id: int
    user_id: int
    document_id: Optional[int] = None
    plugin_id: Optional[str] = None
    action_type: str
    details: Optional[str] = None

class UsageRecordCreate(UsageRecordBase):
    pass

class UsageRecordInDBBase(UsageRecordBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class UsageRecord(UsageRecordInDBBase):
    pass

# Plan details schema
class PlanDetails(BaseModel):
    type: PlanType
    name: str
    description: str
    price_monthly: float
    price_annual: float
    max_users: int
    max_documents: int
    features: List[str]
    recommended_for: str

# Subscription with organization
class SubscriptionWithOrg(Subscription):
    organization: Organization

# Organization with subscription and plugins
class OrganizationWithDetails(Organization):
    subscription: Optional[Subscription] = None
    plugins: List[PluginLicense] = []

# Plugin purchase request
class PluginPurchaseRequest(BaseModel):
    plugin_id: str
    organization_id: int
    billing_cycle: str = "one-time"
    payment_method: str
    payment_details: Dict[str, Any]

# Subscription change request
class SubscriptionChangeRequest(BaseModel):
    organization_id: int
    new_plan_type: PlanType
    billing_cycle: str = "monthly"
    payment_method: str
    payment_details: Dict[str, Any]