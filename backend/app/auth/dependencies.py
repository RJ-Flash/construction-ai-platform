"""
Auth Dependencies

This module contains dependencies for authentication and authorization.
"""
from typing import Optional, List, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.config import get_db
from app.db import crud
from app.auth.security import verify_token
from app.db.models import User as DBUser

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class User:
    """User model."""
    def __init__(self, db_user: DBUser):
        self.id = db_user.id
        self.email = db_user.email
        self.is_active = db_user.is_active
        self.is_admin = db_user.is_admin
        self.first_name = db_user.first_name
        self.last_name = db_user.last_name
        self._db_user = db_user
        
        # Initialize purchased plugins from DB
        self.purchased_plugins = [
            plugin.plugin_id for plugin in db_user.purchased_plugins
            if plugin.is_active
        ]
        
        # Initialize subscription info
        self.subscription_tier = "free"
        self.subscription_expiry = None
        active_subscription = next((s for s in db_user.subscriptions if s.is_active), None)
        if active_subscription:
            self.subscription_tier = active_subscription.tier
            self.subscription_expiry = active_subscription.end_date.isoformat() if active_subscription.end_date else None
        
        # Additional metadata
        self.metadata = {}


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current authenticated user.
    
    Args:
        db: Database session.
        token: The JWT token from the request.
        
    Returns:
        The authenticated user.
        
    Raises:
        HTTPException: If authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise credentials_exception
    
    # Check if user is active
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return User(db_user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active user.
    
    Args:
        current_user: The current user.
        
    Returns:
        The current active user.
        
    Raises:
        HTTPException: If the user is not active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current admin user.
    
    Args:
        current_user: The current user.
        
    Returns:
        The current admin user.
        
    Raises:
        HTTPException: If the user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def has_plugin_access(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
) -> bool:
    """
    Check if a user has access to a plugin.
    
    Args:
        plugin_id: The plugin ID.
        current_user: The current user.
        
    Returns:
        Whether the user has access to the plugin.
    """
    # Admin users have access to all plugins
    if current_user.is_admin:
        return True
    
    # Check if user has explicitly purchased the plugin
    if plugin_id in current_user.purchased_plugins:
        return True
    
    # Check if user's subscription tier includes the plugin
    # Professional tier includes all MEP and structural plugins
    if current_user.subscription_tier == "professional":
        if plugin_id.startswith("mep.") or plugin_id.startswith("structural."):
            return True
    
    # Enterprise tier includes all plugins
    if current_user.subscription_tier == "enterprise":
        return True
    
    return False


async def require_plugin_access(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to require plugin access.
    
    Args:
        plugin_id: The plugin ID.
        current_user: The current user.
        
    Returns:
        The current user if they have access.
        
    Raises:
        HTTPException: If the user does not have access.
    """
    if not await has_plugin_access(plugin_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access to plugin '{plugin_id}' required"
        )
    return current_user
