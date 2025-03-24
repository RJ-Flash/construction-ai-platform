from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import hashlib

from app.db.models.subscription_models import Organization, Subscription, PluginLicense, UsageRecord, PlanType
from app.db.models import User, Document
from app.schemas import subscriptions as schemas

class SubscriptionService:
    """Service for managing subscriptions, organizations, and plugin licenses"""
    
    @staticmethod
    def get_organization(db: Session, organization_id: int) -> Optional[Organization]:
        """Get organization by ID"""
        return db.query(Organization).filter(Organization.id == organization_id).first()
    
    @staticmethod
    def create_organization(db: Session, organization: schemas.OrganizationCreate) -> Organization:
        """Create a new organization"""
        db_organization = Organization(**organization.dict())
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        return db_organization
    
    @staticmethod
    def get_organization_with_subscription(db: Session, organization_id: int) -> Optional[Organization]:
        """Get organization with its subscription info"""
        return db.query(Organization).filter(Organization.id == organization_id).first()
    
    @staticmethod
    def get_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        return db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    @staticmethod
    def get_organization_subscription(db: Session, organization_id: int) -> Optional[Subscription]:
        """Get the subscription for a specific organization"""
        return db.query(Subscription).filter(Subscription.organization_id == organization_id).first()
    
    @staticmethod
    def create_subscription(db: Session, subscription: schemas.SubscriptionCreate) -> Subscription:
        """Create a new subscription for an organization"""
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
    
    @staticmethod
    def update_subscription(
        db: Session, 
        subscription_id: int, 
        subscription_update: schemas.SubscriptionUpdate
    ) -> Optional[Subscription]:
        """Update an existing subscription"""
        db_subscription = SubscriptionService.get_subscription(db, subscription_id)
        if not db_subscription:
            return None
        
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
    
    @staticmethod
    def get_plugin_licenses(db: Session, organization_id: int) -> List[PluginLicense]:
        """Get all plugin licenses for an organization"""
        return db.query(PluginLicense).filter(PluginLicense.organization_id == organization_id).all()
    
    @staticmethod
    def create_plugin_license(db: Session, plugin: schemas.PluginLicenseCreate) -> PluginLicense:
        """Create a new plugin license for an organization"""
        # Generate a unique license key if not provided
        if not plugin.license_key:
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
    
    @staticmethod
    def update_plugin_license(
        db: Session, 
        plugin_id: int, 
        plugin_update: schemas.PluginLicenseUpdate
    ) -> Optional[PluginLicense]:
        """Update an existing plugin license"""
        db_plugin = db.query(PluginLicense).filter(PluginLicense.id == plugin_id).first()
        if not db_plugin:
            return None
        
        # Update plugin with the new data
        update_data = plugin_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_plugin, key, value)
        
        db.commit()
        db.refresh(db_plugin)
        return db_plugin
    
    @staticmethod
    def check_plugin_access(db: Session, organization_id: int, plugin_id: str) -> Tuple[bool, Optional[str]]:
        """Check if an organization has access to a specific plugin"""
        plugin_license = db.query(PluginLicense).filter(
            PluginLicense.organization_id == organization_id,
            PluginLicense.plugin_id == plugin_id,
            PluginLicense.is_active == True
        ).first()
        
        # Check if plugin license exists
        if not plugin_license:
            return False, "No license found"
        
        # Check if plugin license is expired
        if plugin_license.expiry_date and plugin_license.expiry_date < datetime.utcnow():
            return False, "License expired"
        
        return True, None
    
    @staticmethod
    def record_usage(db: Session, usage: schemas.UsageRecordCreate) -> Tuple[UsageRecord, bool]:
        """
        Record a usage event and update relevant counters
        Returns the created usage record and a boolean indicating if limit was exceeded
        """
        # Create the usage record
        db_usage = UsageRecord(**usage.dict())
        db.add(db_usage)
        
        # For document uploads, increment the count in the subscription
        limit_exceeded = False
        if usage.action_type == "document_upload":
            subscription = SubscriptionService.get_organization_subscription(db, usage.organization_id)
            
            if subscription:
                subscription.documents_used += 1
                
                # Check if usage exceeded
                if subscription.documents_used > subscription.max_documents:
                    limit_exceeded = True
        
        db.commit()
        db.refresh(db_usage)
        return db_usage, limit_exceeded
    
    @staticmethod
    def get_organization_usage(db: Session, organization_id: int) -> schemas.PlanUsageInfo:
        """Get usage information for an organization"""
        # Get subscription information
        subscription = SubscriptionService.get_organization_subscription(db, organization_id)
        if not subscription:
            return None
        
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
        
        # Create usage info
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
    
    @staticmethod
    def reset_usage_counters(db: Session, subscription_id: int) -> Optional[Subscription]:
        """Reset usage counters for a subscription (typically done on billing cycle renewal)"""
        subscription = SubscriptionService.get_subscription(db, subscription_id)
        if not subscription:
            return None
        
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
    
    @staticmethod
    def get_subscription_plans() -> List[schemas.SubscriptionPlanInfo]:
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
    
    @staticmethod
    def add_user_to_organization(db: Session, user_id: int, organization_id: int) -> Optional[User]:
        """Add a user to an organization"""
        # Get the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get the organization
        organization = SubscriptionService.get_organization(db, organization_id)
        if not organization:
            return None
        
        # Get the subscription to check user limits
        subscription = SubscriptionService.get_organization_subscription(db, organization_id)
        if subscription:
            current_user_count = db.query(User).filter(User.organization_id == organization_id).count()
            if current_user_count >= subscription.max_users:
                return None  # User limit exceeded
        
        # Add user to organization
        user.organization_id = organization_id
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def remove_user_from_organization(db: Session, user_id: int) -> Optional[User]:
        """Remove a user from their organization"""
        # Get the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.organization_id:
            return None
        
        # Remove user from organization
        user.organization_id = None
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def check_document_upload_allowed(db: Session, organization_id: int) -> Tuple[bool, Optional[str]]:
        """Check if an organization is allowed to upload more documents"""
        subscription = SubscriptionService.get_organization_subscription(db, organization_id)
        if not subscription:
            return False, "No subscription found"
        
        # Check if subscription is active
        if not subscription.is_active:
            return False, "Subscription is not active"
        
        # Check if subscription has expired
        if subscription.end_date and subscription.end_date < datetime.utcnow():
            return False, "Subscription has expired"
        
        # Check document limit
        if subscription.documents_used >= subscription.max_documents:
            return False, f"Document limit reached ({subscription.max_documents})"
        
        return True, None
    
    @staticmethod
    def check_subscription_expiry_status(db: Session, subscription_id: int) -> dict:
        """Check the expiry status of a subscription"""
        subscription = SubscriptionService.get_subscription(db, subscription_id)
        if not subscription:
            return {"status": "error", "message": "Subscription not found"}
        
        today = datetime.utcnow()
        
        # Calculate days remaining
        days_remaining = 0
        if subscription.end_date:
            delta = subscription.end_date - today
            days_remaining = delta.days
        
        # Determine status
        status = "active"
        if not subscription.is_active:
            status = "inactive"
        elif subscription.end_date and subscription.end_date < today:
            status = "expired"
        elif days_remaining <= 7:
            status = "expiring_soon"
        
        return {
            "status": status,
            "days_remaining": days_remaining,
            "end_date": subscription.end_date,
            "is_active": subscription.is_active,
            "plan_type": subscription.plan_type
        }
