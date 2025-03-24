from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models.subscription_models import Organization, Subscription, PluginLicense, UsageRecord, PlanType
from app.db.models import User
from app.schemas import subscriptions as schemas
from app.core.security import get_current_active_user, get_current_admin_user

router = APIRouter()

# Get organization details
@router.get("/{organization_id}", response_model=schemas.OrganizationWithSubscription)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user belongs to this organization
    if current_user.organization_id != organization_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization's data",
        )
    
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    return organization

# Create organization
@router.post("/", response_model=schemas.Organization)
def create_organization(
    organization: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    db_organization = Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization

# Get subscription details
@router.get("/subscription/{subscription_id}", response_model=schemas.Subscription)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    # Check if user has permission to view this subscription
    if current_user.organization_id != subscription.organization_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this subscription data",
        )
    
    return subscription

# Create subscription
@router.post("/subscription/", response_model=schemas.Subscription)
def create_subscription(
    subscription: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    # Check if organization exists
    organization = db.query(Organization).filter(Organization.id == subscription.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Check if subscription already exists for this organization
    existing_subscription = db.query(Subscription).filter(
        Subscription.organization_id == subscription.organization_id
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This organization already has a subscription",
        )
    
    # Set end date based on billing cycle if not provided
    if not subscription.end_date:
        if subscription.billing_cycle == "monthly":
            subscription.end_date = subscription.start_date + timedelta(days=30)
        elif subscription.billing_cycle == "annual":
            subscription.end_date = subscription.start_date + timedelta(days=365)
    
    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

# Update subscription
@router.put("/subscription/{subscription_id}", response_model=schemas.Subscription)
def update_subscription(
    subscription_id: int,
    subscription_update: schemas.SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    # Update subscription with the new data
    update_data = subscription_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_subscription, key, value)
    
    # Update end date if billing cycle changes
    if 'billing_cycle' in update_data and not 'end_date' in update_data:
        if update_data['billing_cycle'] == "monthly":
            db_subscription.end_date = db_subscription.start_date + timedelta(days=30)
        elif update_data['billing_cycle'] == "annual":
            db_subscription.end_date = db_subscription.start_date + timedelta(days=365)
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

# Get plugin licenses for an organization
@router.get("/plugins/{organization_id}", response_model=List[schemas.PluginLicense])
def get_organization_plugins(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user belongs to this organization
    if current_user.organization_id != organization_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization's plugins",
        )
    
    plugins = db.query(PluginLicense).filter(PluginLicense.organization_id == organization_id).all()
    return plugins

# Create plugin license
@router.post("/plugins/", response_model=schemas.PluginLicense)
def create_plugin_license(
    plugin: schemas.PluginLicenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    # Check if organization exists
    organization = db.query(Organization).filter(Organization.id == plugin.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Generate a unique license key if not provided
    if not plugin.license_key:
        import uuid
        import hashlib
        unique_id = str(uuid.uuid4()) + str(plugin.organization_id) + plugin.plugin_id
        plugin.license_key = hashlib.sha256(unique_id.encode()).hexdigest()[:32]
    
    # Set expiry date based on billing cycle if not provided
    if not plugin.expiry_date and plugin.billing_cycle != "one-time":
        if plugin.billing_cycle == "monthly":
            plugin.expiry_date = plugin.purchase_date + timedelta(days=30)
        elif plugin.billing_cycle == "annual":
            plugin.expiry_date = plugin.purchase_date + timedelta(days=365)
    
    db_plugin = PluginLicense(**plugin.dict())
    db.add(db_plugin)
    db.commit()
    db.refresh(db_plugin)
    return db_plugin

# Update plugin license
@router.put("/plugins/{plugin_id}", response_model=schemas.PluginLicense)
def update_plugin_license(
    plugin_id: int,
    plugin_update: schemas.PluginLicenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    db_plugin = db.query(PluginLicense).filter(PluginLicense.id == plugin_id).first()
    if not db_plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin license not found",
        )
    
    # Update plugin with the new data
    update_data = plugin_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plugin, key, value)
    
    db.commit()
    db.refresh(db_plugin)
    return db_plugin

# Record usage
@router.post("/usage/", response_model=schemas.UsageRecord)
def record_usage(
    usage: schemas.UsageRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user belongs to the specified organization
    if current_user.organization_id != usage.organization_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to record usage for this organization",
        )
    
    # Check if organization exists
    organization = db.query(Organization).filter(Organization.id == usage.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # For document uploads, increment the count in the subscription
    if usage.action_type == "document_upload":
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == usage.organization_id
        ).first()
        
        if subscription:
            subscription.documents_used += 1
            
            # Check if usage exceeded
            if subscription.documents_used > subscription.max_documents:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Document limit exceeded for current subscription plan",
                )
    
    db_usage = UsageRecord(**usage.dict())
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    return db_usage

# Get subscription plans info
@router.get("/plans/", response_model=List[schemas.SubscriptionPlanInfo])
def get_subscription_plans():
    """Return information about all available subscription plans"""
    
    # Define the subscription plans based on the README.md pricing table
    plans = [
        {
            "plan_type": PlanType.FREE,
            "name": "Free",
            "description": "Basic plan with limited features",
            "price_monthly": 0,
            "price_annual": 0,
            "max_users": 1,
            "max_documents": 1,
            "features": ["1 PDF per month", "Basic element extraction", "AI analysis"]
        },
        {
            "plan_type": PlanType.STARTER,
            "name": "Starter",
            "description": "Small projects and individuals",
            "price_monthly": 49,
            "price_annual": 529,  # 10% discount for annual billing
            "max_users": 1,
            "max_documents": 5,
            "features": ["5 PDFs per month", "Element extraction", "AI analysis", "Quote generation"]
        },
        {
            "plan_type": PlanType.ESSENTIAL,
            "name": "Essential",
            "description": "Small to medium businesses",
            "price_monthly": 129,
            "price_annual": 1393,  # 10% discount
            "max_users": 3,
            "max_documents": 10,
            "features": ["10 documents per month", "PDF, CAD & BIM support", "Element extraction", "Quote generation", "1 specialized plugin included"]
        },
        {
            "plan_type": PlanType.PROFESSIONAL,
            "name": "Professional",
            "description": "Medium-sized contractors",
            "price_monthly": 249,
            "price_annual": 2690,  # 10% discount
            "max_users": 5,
            "max_documents": 20,
            "features": ["20 documents per month", "PDF, CAD & BIM support", "Priority analysis", "Quote generation", "2 specialized plugins included"]
        },
        {
            "plan_type": PlanType.ADVANCED,
            "name": "Advanced",
            "description": "Large construction businesses",
            "price_monthly": 599,
            "price_annual": 5990,  # ~15% discount
            "max_users": 10,
            "max_documents": 40,
            "features": ["40 documents per month", "All file formats supported", "Priority analysis", "Advanced quote generation", "3 specialized plugins included", "API access"]
        },
        {
            "plan_type": PlanType.ULTIMATE,
            "name": "Ultimate",
            "description": "Enterprise solution for large companies",
            "price_monthly": 999,
            "price_annual": 9990,  # ~15% discount
            "max_users": 999,  # Virtually unlimited
            "max_documents": 999,  # Customizable
            "features": ["Unlimited documents", "All features included", "All file formats supported", "Priority support", "Custom integrations", "All plugins included", "API access", "Custom training"]
        }
    ]
    
    return [schemas.SubscriptionPlanInfo(**plan) for plan in plans]

# Get usage info for an organization
@router.get("/usage/{organization_id}", response_model=schemas.PlanUsageInfo)
def get_organization_usage(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user belongs to this organization
    if current_user.organization_id != organization_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization's usage data",
        )
    
    # Get subscription information
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == organization_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for this organization",
        )
    
    # Get user count
    users_count = db.query(User).filter(User.organization_id == organization_id).count()
    
    # Get active plugins
    plugins = db.query(PluginLicense).filter(
        PluginLicense.organization_id == organization_id,
        PluginLicense.is_active == True
    ).all()
    
    # Calculate percentages
    documents_percentage = (subscription.documents_used / subscription.max_documents * 100) if subscription.max_documents > 0 else 0
    users_percentage = (users_count / subscription.max_users * 100) if subscription.max_users > 0 else 0
    
    # Return usage info
    usage_info = {
        "documents_used": subscription.documents_used,
        "documents_total": subscription.max_documents,
        "documents_percentage": documents_percentage,
        "users_used": users_count,
        "users_total": subscription.max_users,
        "users_percentage": users_percentage,
        "active_plugins": [plugin.plugin_name for plugin in plugins]
    }
    
    return schemas.PlanUsageInfo(**usage_info)

# Check if an organization can use a specific plugin
@router.get("/plugins/{organization_id}/check/{plugin_id}")
def check_plugin_access(
    organization_id: int,
    plugin_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user belongs to this organization
    if current_user.organization_id != organization_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check plugin access for this organization",
        )
    
    # Check if organization has a valid license for this plugin
    plugin_license = db.query(PluginLicense).filter(
        PluginLicense.organization_id == organization_id,
        PluginLicense.plugin_id == plugin_id,
        PluginLicense.is_active == True
    ).first()
    
    # Check if plugin license is expired
    if plugin_license and plugin_license.expiry_date and plugin_license.expiry_date < datetime.utcnow():
        return {"has_access": False, "reason": "License expired"}
    
    if plugin_license:
        return {"has_access": True}
    else:
        return {"has_access": False, "reason": "No valid license found"}

# Reset usage counters (for monthly billing cycle)
@router.post("/subscription/{subscription_id}/reset-usage", response_model=schemas.Subscription)
def reset_usage_counters(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    # Reset the document usage counter
    subscription.documents_used = 0
    
    # Update the end date based on the billing cycle
    if subscription.billing_cycle == "monthly":
        subscription.end_date = datetime.utcnow() + timedelta(days=30)
    elif subscription.billing_cycle == "annual":
        subscription.end_date = datetime.utcnow() + timedelta(days=365)
    
    db.commit()
    db.refresh(subscription)
    return subscription
