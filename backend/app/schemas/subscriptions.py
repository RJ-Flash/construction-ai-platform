from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Subscription plan enum
class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    ESSENTIAL = "essential"
    PROFESSIONAL = "professional"
    ADVANCED = "advanced"
    ULTIMATE = "ultimate"

# Organization base model
class OrganizationBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

# Organization create model
class OrganizationCreate(OrganizationBase):
    pass

# Organization in DB
class Organization(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Subscription base model
class SubscriptionBase(BaseModel):
    plan_type: PlanType
    is_active: bool = True
    is_trial: bool = False
    max_users: int
    max_documents: int
    documents_used: int = 0
    price: float
    billing_cycle: str  # monthly or annual
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None

# Subscription create model
class SubscriptionCreate(SubscriptionBase):
    organization_id: int
    start_date: datetime = datetime.utcnow()
    end_date: Optional[datetime] = None

# Subscription update model
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

# Subscription in DB
class Subscription(SubscriptionBase):
    id: int
    organization_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Plugin license base model
class PluginLicenseBase(BaseModel):
    plugin_id: str
    plugin_name: str
    is_active: bool = True
    price: float
    billing_cycle: str  # one-time, monthly, annual

# Plugin license create model
class PluginLicenseCreate(PluginLicenseBase):
    organization_id: int
    purchase_date: datetime = datetime.utcnow()
    expiry_date: Optional[datetime] = None
    license_key: Optional[str] = None
    payment_id: Optional[str] = None

# Plugin license update model
class PluginLicenseUpdate(BaseModel):
    is_active: Optional[bool] = None
    expiry_date: Optional[datetime] = None
    price: Optional[float] = None
    billing_cycle: Optional[str] = None
    payment_id: Optional[str] = None

# Plugin license in DB
class PluginLicense(PluginLicenseBase):
    id: int
    organization_id: int
    license_key: str
    purchase_date: datetime
    expiry_date: Optional[datetime] = None
    payment_id: Optional[str] = None
    
    class Config:
        orm_mode = True

# Usage record base model
class UsageRecordBase(BaseModel):
    organization_id: int
    user_id: int
    action_type: str  # document_upload, document_analysis, plugin_usage
    document_id: Optional[int] = None
    plugin_id: Optional[str] = None
    details: Optional[str] = None

# Usage record create model
class UsageRecordCreate(UsageRecordBase):
    timestamp: datetime = datetime.utcnow()

# Usage record in DB
class UsageRecord(UsageRecordBase):
    id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True

# Organization with subscription
class OrganizationWithSubscription(Organization):
    subscription: Optional[Subscription] = None
    plugins: List[PluginLicense] = []

# Subscription plan info
class SubscriptionPlanInfo(BaseModel):
    plan_type: PlanType
    name: str
    description: str
    price_monthly: float
    price_annual: float
    max_users: int
    max_documents: int
    features: List[str]
    plugin_discounts: Dict[str, float] = {}

# Plan usage info
class PlanUsageInfo(BaseModel):
    documents_used: int
    documents_total: int
    documents_percentage: float
    users_used: int
    users_total: int
    users_percentage: float
    active_plugins: List[str] = []

# Subscription with usage
class SubscriptionWithUsage(Subscription):
    usage: PlanUsageInfo
    organization: Organization