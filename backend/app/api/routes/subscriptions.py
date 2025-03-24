from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ...db.database import get_db
from ...db.models import User, Organization, Subscription, PluginLicense, UsageRecord, PlanType
from ...schemas import User as UserSchema
from ...schemas.subscriptions import (
    Organization as OrganizationSchema,
    OrganizationCreate,
    OrganizationUpdate,
    Subscription as SubscriptionSchema,
    SubscriptionCreate,
    SubscriptionUpdate,
    PluginLicense as PluginLicenseSchema,
    PluginLicenseCreate,
    PluginLicenseUpdate,
    PlanDetails,
    SubscriptionChangeRequest,
    PluginPurchaseRequest,
    OrganizationWithDetails
)
from ...core.auth import get_current_active_user

router = APIRouter()

# Plan details - based on the pricing strategy defined in the project
PLAN_DETAILS = {
    PlanType.FREE: {
        "type": PlanType.FREE,
        "name": "Free Plan",
        "description": "Try out the platform with basic features",
        "price_monthly": 0,
        "price_annual": 0,
        "max_users": 1,
        "max_documents": 1,
        "features": [
            "1 PDF per month",
            "Basic document analysis",
            "Limited element extraction",
            "Manual quote generation"
        ],
        "recommended_for": "Trial users and small-scale testing"
    },
    PlanType.STARTER: {
        "type": PlanType.STARTER,
        "name": "Starter Plan",
        "description": "Perfect for small businesses just getting started",
        "price_monthly": 49,
        "price_annual": 529,  # 10% discount on annual
        "max_users": 2,
        "max_documents": 5,
        "features": [
            "5 PDFs per month",
            "Standard document analysis",
            "Basic element extraction",
            "Simple quote generation",
            "Email support"
        ],
        "recommended_for": "Small businesses or independent contractors"
    },
    PlanType.ESSENTIAL: {
        "type": PlanType.ESSENTIAL,
        "name": "Essential Plan",
        "description": "Comprehensive features for growing businesses",
        "price_monthly": 129,
        "price_annual": 1393,  # 10% discount on annual
        "max_users": 3,
        "max_documents": 10,
        "features": [
            "10 documents per month (PDF, CAD, BIM)",
            "Advanced document analysis",
            "Full element extraction",
            "Comprehensive quote generation",
            "Email and chat support",
            "Basic plugin access"
        ],
        "recommended_for": "Small-to-medium contractors"
    },
    PlanType.PROFESSIONAL: {
        "type": PlanType.PROFESSIONAL,
        "name": "Professional Plan",
        "description": "Full-featured for professional construction teams",
        "price_monthly": 249,
        "price_annual": 2690,  # 10% discount on annual
        "max_users": 5,
        "max_documents": 20,
        "features": [
            "20 documents per month (PDF, CAD, BIM)",
            "Premium document analysis",
            "Enhanced element extraction",
            "Advanced quote generation with templates",
            "Priority support",
            "Advanced analytics",
            "Access to all basic plugins"
        ],
        "recommended_for": "Medium-sized construction firms"
    },
    PlanType.ADVANCED: {
        "type": PlanType.ADVANCED,
        "name": "Advanced Plan",
        "description": "Enterprise-grade features for larger teams",
        "price_monthly": 599,
        "price_annual": 6100,  # 15% discount on annual
        "max_users": 10,
        "max_documents": 50,
        "features": [
            "50 documents per month (all formats)",
            "Enterprise-grade document analysis",
            "Premium element extraction",
            "Custom quote generation",
            "Dedicated account manager",
            "Advanced analytics and reporting",
            "Access to premium plugins",
            "API access"
        ],
        "recommended_for": "Larger teams or companies"
    },
    PlanType.ULTIMATE: {
        "type": PlanType.ULTIMATE,
        "name": "Ultimate Plan",
        "description": "Custom enterprise solution",
        "price_monthly": 0,  # Custom pricing
        "price_annual": 0,  # Custom pricing
        "max_users": 999,  # Unlimited
        "max_documents": 999,  # Custom
        "features": [
            "Custom document allowances",
            "Unlimited user seats",
            "All features from Advanced plan",
            "Custom integrations",
            "Dedicated support team",
            "Access to all plugins",
            "Custom feature development",
            "On-premises deployment option"
        ],
        "recommended_for": "Large organizations or enterprises"
    }
}

@router.get("/plans", response_model=List[PlanDetails])
async def get_all_plans(
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get details of all available subscription plans.
    """
    return [PlanDetails(**plan_data) for plan_data in PLAN_DETAILS.values()]

@router.get("/plans/{plan_type}", response_model=PlanDetails)
async def get_plan_details(
    plan_type: PlanType,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get details of a specific subscription plan.
    """
    if plan_type not in PLAN_DETAILS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan type '{plan_type}' not found"
        )
        
    return PlanDetails(**PLAN_DETAILS[plan_type])

@router.get("/organizations", response_model=List[OrganizationSchema])
async def get_organizations(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get all organizations that the current user has access to.
    """
    # For now, only return organizations the user is part of
    return db.query(Organization).filter(
        Organization.users.any(id=current_user.id)
    ).all()

@router.post("/organizations", response_model=OrganizationSchema, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Create a new organization.
    """
    # Check if email is already used
    if db.query(Organization).filter(Organization.email == org_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Create organization
    db_org = Organization(**org_data.dict())
    
    # Add current user to organization
    db_user = db.query(User).filter(User.id == current_user.id).first()
    db_user.organization = db_org
    
    # Create free subscription
    free_plan = SubscriptionCreate(
        organization_id=0,  # Will be updated after commit
        plan_type=PlanType.FREE,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=365),  # 1 year free trial
        is_trial=True
    )
    db_subscription = Subscription(**free_plan.dict(exclude={"organization_id"}))
    db_org.subscription = db_subscription
    
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    
    # Update subscription organization_id
    db_subscription.organization_id = db_org.id
    db.commit()
    
    return db_org

@router.get("/organizations/{org_id}", response_model=OrganizationWithDetails)
async def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get details of a specific organization, including subscription and plugins.
    """
    db_org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not db_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
        
    # Check if user has access
    if not db.query(User).filter(User.id == current_user.id, User.organization_id == org_id).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this organization"
        )
        
    return db_org

@router.put("/organizations/{org_id}", response_model=OrganizationSchema)
async def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Update an organization's details.
    """
    db_org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not db_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
        
    # Check if user has access
    if not db.query(User).filter(User.id == current_user.id, User.organization_id == org_id).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this organization"
        )
        
    # Update organization fields
    for field, value in org_data.dict(exclude_unset=True).items():
        setattr(db_org, field, value)
        
    db.commit()
    db.refresh(db_org)
    
    return db_org

@router.post("/subscriptions/change", response_model=SubscriptionSchema)
async def change_subscription_plan(
    change_request: SubscriptionChangeRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Change an organization's subscription plan.
    """
    # Check if user has access to the organization
    if not db.query(User).filter(User.id == current_user.id, User.organization_id == change_request.organization_id).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this organization's subscription"
        )
        
    # Get current subscription
    db_subscription = db.query(Subscription).filter(
        Subscription.organization_id == change_request.organization_id
    ).first()
    
    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
        
    # Get new plan details
    if change_request.new_plan_type not in PLAN_DETAILS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan type: {change_request.new_plan_type}"
        )
        
    plan_details = PLAN_DETAILS[change_request.new_plan_type]
    
    # Set pricing based on billing cycle
    price = plan_details["price_monthly"]
    if change_request.billing_cycle == "annual":
        price = plan_details["price_annual"]
        
    # For Ultimate plan, price needs to be specified or else it's a sales inquiry
    if change_request.new_plan_type == PlanType.ULTIMATE and price == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ultimate plan requires custom pricing. Please contact sales."
        )
        
    # Update subscription
    db_subscription.plan_type = change_request.new_plan_type
    db_subscription.max_users = plan_details["max_users"]
    db_subscription.max_documents = plan_details["max_documents"]
    db_subscription.price = price
    db_subscription.billing_cycle = change_request.billing_cycle
    db_subscription.payment_method = change_request.payment_method
    
    # Set end date based on billing cycle
    if change_request.billing_cycle == "annual":
        db_subscription.end_date = datetime.utcnow() + timedelta(days=365)
    else:  # monthly
        db_subscription.end_date = datetime.utcnow() + timedelta(days=30)
        
    db_subscription.is_active = True
    db_subscription.is_trial = False
    db_subscription.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription

@router.post("/plugins/purchase", response_model=PluginLicenseSchema)
async def purchase_plugin(
    purchase_request: PluginPurchaseRequest,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Purchase a plugin license for an organization.
    """
    # Check if user has access to the organization
    if not db.query(User).filter(User.id == current_user.id, User.organization_id == purchase_request.organization_id).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to purchase plugins for this organization"
        )
        
    # Check if plugin is already licensed
    existing_license = db.query(PluginLicense).filter(
        PluginLicense.organization_id == purchase_request.organization_id,
        PluginLicense.plugin_id == purchase_request.plugin_id,
        PluginLicense.is_active == True
    ).first()
    
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization already has an active license for this plugin"
        )
        
    # Get plugin details
    # In a real implementation, this would fetch from a plugin repository
    # For now, we'll use a simplified approach
    from ...plugins.registry import get_plugin_by_id
    
    plugin_class = get_plugin_by_id(purchase_request.plugin_id)
    if not plugin_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin with ID '{purchase_request.plugin_id}' not found"
        )
        
    # Create temporary plugin instance to get metadata
    plugin = plugin_class()
    plugin_metadata = plugin.metadata
    
    # Generate license key (in production, this would be more sophisticated)
    import uuid
    license_key = str(uuid.uuid4())
    
    # Create license
    license_data = PluginLicenseCreate(
        organization_id=purchase_request.organization_id,
        plugin_id=purchase_request.plugin_id,
        plugin_name=plugin_metadata["name"],
        license_key=license_key,
        purchase_date=datetime.utcnow(),
        price=plugin_metadata["price"],
        billing_cycle=purchase_request.billing_cycle
    )
    
    # Set expiry date based on billing cycle
    if purchase_request.billing_cycle == "annual":
        license_data.expiry_date = datetime.utcnow() + timedelta(days=365)
    elif purchase_request.billing_cycle == "monthly":
        license_data.expiry_date = datetime.utcnow() + timedelta(days=30)
    
    db_license = PluginLicense(**license_data.dict())
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    
    return db_license