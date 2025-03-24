import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.models.subscription_models import Organization, Subscription, PluginLicense, UsageRecord, PlanType
from app.db.models import User
from app.services.subscription_service import SubscriptionService

def test_organization_creation(db: Session):
    # Create a test organization
    org_data = {
        "name": "Test Organization",
        "email": "test@testorg.com",
        "phone": "123-456-7890",
        "address": "123 Test Street"
    }
    
    organization = Organization(**org_data)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    # Verify the organization was created
    assert organization.id is not None
    assert organization.name == "Test Organization"
    assert organization.email == "test@testorg.com"
    
    # Clean up
    db.delete(organization)
    db.commit()

def test_subscription_creation(db: Session):
    # Create a test organization
    organization = Organization(
        name="Test Organization", 
        email="test@testorg.com"
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    # Create a subscription for the organization
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=30)
    
    subscription = Subscription(
        organization_id=organization.id,
        plan_type=PlanType.STARTER,
        is_active=True,
        max_users=1,
        max_documents=5,
        price=49.00,
        billing_cycle="monthly",
        start_date=start_date,
        end_date=end_date
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Verify the subscription was created
    assert subscription.id is not None
    assert subscription.organization_id == organization.id
    assert subscription.plan_type == PlanType.STARTER
    assert subscription.max_documents == 5
    
    # Clean up
    db.delete(subscription)
    db.delete(organization)
    db.commit()

def test_plugin_license_creation(db: Session):
    # Create a test organization
    organization = Organization(
        name="Test Organization", 
        email="test@testorg.com"
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    # Create a plugin license
    purchase_date = datetime.utcnow()
    expiry_date = purchase_date + timedelta(days=365)
    
    plugin_license = PluginLicense(
        organization_id=organization.id,
        plugin_id="concrete-structures",
        plugin_name="Concrete Structures Plugin",
        is_active=True,
        license_key="TEST-LICENSE-KEY-12345",
        price=199.00,
        billing_cycle="annual",
        purchase_date=purchase_date,
        expiry_date=expiry_date
    )
    
    db.add(plugin_license)
    db.commit()
    db.refresh(plugin_license)
    
    # Verify the plugin license was created
    assert plugin_license.id is not None
    assert plugin_license.organization_id == organization.id
    assert plugin_license.plugin_name == "Concrete Structures Plugin"
    assert plugin_license.license_key == "TEST-LICENSE-KEY-12345"
    
    # Clean up
    db.delete(plugin_license)
    db.delete(organization)
    db.commit()

def test_usage_tracking(db: Session):
    # Create a test organization with subscription
    organization = Organization(
        name="Test Organization", 
        email="test@testorg.com"
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    subscription = Subscription(
        organization_id=organization.id,
        plan_type=PlanType.ESSENTIAL,
        is_active=True,
        max_users=3,
        max_documents=10,
        documents_used=0,
        price=129.00,
        billing_cycle="monthly"
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpwd",
        organization_id=organization.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Record document upload usage
    usage_record = UsageRecord(
        organization_id=organization.id,
        user_id=user.id,
        action_type="document_upload",
        details="Test document upload"
    )
    
    db.add(usage_record)
    db.commit()
    db.refresh(usage_record)
    
    # Use the service to record usage and update counters
    from app.schemas.subscriptions import UsageRecordCreate
    
    for i in range(3):  # Add 3 more usage records
        usage_create = UsageRecordCreate(
            organization_id=organization.id,
            user_id=user.id,
            action_type="document_upload",
            details=f"Test document upload {i+1}"
        )
        
        record, limit_exceeded = SubscriptionService.record_usage(db, usage_create)
        assert not limit_exceeded
    
    # Refresh subscription to get updated documents_used
    db.refresh(subscription)
    
    # Check if documents_used has been incremented
    assert subscription.documents_used == 3
    
    # Clean up
    db.query(UsageRecord).filter(UsageRecord.organization_id == organization.id).delete()
    db.delete(user)
    db.delete(subscription)
    db.delete(organization)
    db.commit()

def test_document_limit_enforcement(db: Session):
    # Create a test organization with subscription - only 2 documents allowed
    organization = Organization(
        name="Test Organization", 
        email="test@testorg.com"
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    subscription = Subscription(
        organization_id=organization.id,
        plan_type=PlanType.FREE,
        is_active=True,
        max_users=1,
        max_documents=2,  # Limited to 2 documents
        documents_used=0,
        price=0.00,
        billing_cycle="monthly"
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpwd",
        organization_id=organization.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Use the service to record usage and update counters
    from app.schemas.subscriptions import UsageRecordCreate
    
    # First 2 uploads should be allowed
    for i in range(2):
        usage_create = UsageRecordCreate(
            organization_id=organization.id,
            user_id=user.id,
            action_type="document_upload",
            details=f"Test document upload {i+1}"
        )
        
        record, limit_exceeded = SubscriptionService.record_usage(db, usage_create)
        assert not limit_exceeded
    
    # The 3rd upload should exceed the limit
    usage_create = UsageRecordCreate(
        organization_id=organization.id,
        user_id=user.id,
        action_type="document_upload",
        details="Test document upload 3"
    )
    
    record, limit_exceeded = SubscriptionService.record_usage(db, usage_create)
    assert limit_exceeded
    
    # Check if documents_used has been incremented to 3
    db.refresh(subscription)
    assert subscription.documents_used == 3
    
    # Check if upload is allowed directly using the service
    allowed, reason = SubscriptionService.check_document_upload_allowed(db, organization.id)
    assert not allowed
    assert "Document limit reached" in reason
    
    # Clean up
    db.query(UsageRecord).filter(UsageRecord.organization_id == organization.id).delete()
    db.delete(user)
    db.delete(subscription)
    db.delete(organization)
    db.commit()

def test_plugin_access_check(db: Session):
    # Create a test organization
    organization = Organization(
        name="Test Organization", 
        email="test@testorg.com"
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    # Create an active plugin license
    active_plugin = PluginLicense(
        organization_id=organization.id,
        plugin_id="walls-plugin",
        plugin_name="Walls Plugin",
        is_active=True,
        license_key="ACTIVE-LICENSE-KEY",
        billing_cycle="annual",
        expiry_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # Create an expired plugin license
    expired_plugin = PluginLicense(
        organization_id=organization.id,
        plugin_id="doors-plugin",
        plugin_name="Doors Plugin",
        is_active=True,
        license_key="EXPIRED-LICENSE-KEY",
        billing_cycle="annual",
        expiry_date=datetime.utcnow() - timedelta(days=10)  # Expired 10 days ago
    )
    
    # Create an inactive plugin license
    inactive_plugin = PluginLicense(
        organization_id=organization.id,
        plugin_id="windows-plugin",
        plugin_name="Windows Plugin",
        is_active=False,  # Inactive
        license_key="INACTIVE-LICENSE-KEY",
        billing_cycle="annual",
        expiry_date=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(active_plugin)
    db.add(expired_plugin)
    db.add(inactive_plugin)
    db.commit()
    
    # Check access for active plugin - should be allowed
    has_access, reason = SubscriptionService.check_plugin_access(db, organization.id, "walls-plugin")
    assert has_access is True
    assert reason is None
    
    # Check access for expired plugin - should be denied
    has_access, reason = SubscriptionService.check_plugin_access(db, organization.id, "doors-plugin")
    assert has_access is False
    assert reason == "License expired"
    
    # Check access for inactive plugin - should be denied
    has_access, reason = SubscriptionService.check_plugin_access(db, organization.id, "windows-plugin")
    assert has_access is False
    assert reason == "No license found"
    
    # Check access for non-existent plugin - should be denied
    has_access, reason = SubscriptionService.check_plugin_access(db, organization.id, "nonexistent-plugin")
    assert has_access is False
    assert reason == "No license found"
    
    # Clean up
    db.delete(active_plugin)
    db.delete(expired_plugin)
    db.delete(inactive_plugin)
    db.delete(organization)
    db.commit()
