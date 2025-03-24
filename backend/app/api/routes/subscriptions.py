from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models.subscription_models import Organization, Subscription, PluginLicense, UsageRecord
from app.db.models import User
from app.schemas import subscriptions as schemas
from app.core.security import get_current_active_user, get_current_admin_user
from app.services.subscription_service import SubscriptionService

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
    
    organization = SubscriptionService.get_organization_with_subscription(db, organization_id)
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
    return SubscriptionService.create_organization(db, organization)

# Get subscription details
@router.get("/subscription/{subscription_id}", response_model=schemas.Subscription)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    subscription = SubscriptionService.get_subscription(db, subscription_id)
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
    organization = SubscriptionService.get_organization(db, subscription.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Check if subscription already exists for this organization
    existing_subscription = SubscriptionService.get_organization_subscription(db, subscription.organization_id)
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This organization already has a subscription",
        )
    
    return SubscriptionService.create_subscription(db, subscription)

# Update subscription
@router.put("/subscription/{subscription_id}", response_model=schemas.Subscription)
def update_subscription(
    subscription_id: int,
    subscription_update: schemas.SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    updated_subscription = SubscriptionService.update_subscription(db, subscription_id, subscription_update)
    if not updated_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    return updated_subscription

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
    
    return SubscriptionService.get_plugin_licenses(db, organization_id)

# Create plugin license
@router.post("/plugins/", response_model=schemas.PluginLicense)
def create_plugin_license(
    plugin: schemas.PluginLicenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    # Check if organization exists
    organization = SubscriptionService.get_organization(db, plugin.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    return SubscriptionService.create_plugin_license(db, plugin)

# Update plugin license
@router.put("/plugins/{plugin_id}", response_model=schemas.PluginLicense)
def update_plugin_license(
    plugin_id: int,
    plugin_update: schemas.PluginLicenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    updated_plugin = SubscriptionService.update_plugin_license(db, plugin_id, plugin_update)
    if not updated_plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin license not found",
        )
    
    return updated_plugin

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
    organization = SubscriptionService.get_organization(db, usage.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    usage_record, limit_exceeded = SubscriptionService.record_usage(db, usage)
    
    if limit_exceeded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document limit exceeded for current subscription plan",
        )
    
    return usage_record

# Get subscription plans info
@router.get("/plans/", response_model=List[schemas.SubscriptionPlanInfo])
def get_subscription_plans():
    """Return information about all available subscription plans"""
    return SubscriptionService.get_subscription_plans()

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
    
    usage_info = SubscriptionService.get_organization_usage(db, organization_id)
    if not usage_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for this organization",
        )
    
    return usage_info

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
    
    has_access, reason = SubscriptionService.check_plugin_access(db, organization_id, plugin_id)
    
    if has_access:
        return {"has_access": True}
    else:
        return {"has_access": False, "reason": reason}

# Reset usage counters (for monthly billing cycle)
@router.post("/subscription/{subscription_id}/reset-usage", response_model=schemas.Subscription)
def reset_usage_counters(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    subscription = SubscriptionService.reset_usage_counters(db, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    return subscription

# Add user to organization
@router.post("/organization/{organization_id}/users/{user_id}")
def add_user_to_organization(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = SubscriptionService.add_user_to_organization(db, user_id, organization_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add user to organization. User may not exist or user limit exceeded.",
        )
    
    return {"status": "success", "message": "User added to organization"}

# Remove user from organization
@router.delete("/organization/users/{user_id}")
def remove_user_from_organization(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = SubscriptionService.remove_user_from_organization(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or not assigned to any organization",
        )
    
    return {"status": "success", "message": "User removed from organization"}

# Check subscription expiry status
@router.get("/subscription/{subscription_id}/expiry-status")
def check_subscription_expiry_status(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Get the subscription
    subscription = SubscriptionService.get_subscription(db, subscription_id)
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
    
    return SubscriptionService.check_subscription_expiry_status(db, subscription_id)

# Check if document upload is allowed for an organization
@router.get("/organization/{organization_id}/can-upload-document")
def check_document_upload_allowed(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user belongs to this organization
    if current_user.organization_id != organization_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check upload permissions for this organization",
        )
    
    allowed, reason = SubscriptionService.check_document_upload_allowed(db, organization_id)
    
    return {"allowed": allowed, "reason": reason if not allowed else None}
