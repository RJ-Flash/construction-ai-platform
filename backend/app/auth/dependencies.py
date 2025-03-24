"""
Auth Dependencies

This module contains dependencies for authentication and authorization.
"""
from typing import Optional, List, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
import jwt
from jwt.exceptions import PyJWTError

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT
# In a real application, this would be stored securely and not in code
SECRET_KEY = "super_secret_key_that_should_be_env_var"
ALGORITHM = "HS256"


class User(BaseModel):
    """User model."""
    id: str
    email: str
    is_active: bool = True
    is_admin: bool = False
    purchased_plugins: List[str] = Field(default_factory=list)
    subscription_tier: str = "free"
    subscription_expiry: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the current authenticated user.
    
    Args:
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
    
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # In a real application, we would fetch the user from a database
        # For now, we'll just create a dummy user with the ID from the token
        user = User(
            id=user_id,
            email=f"{user_id}@example.com",
            purchased_plugins=["mep.electrical_systems", "mep.plumbing_systems", "mep.hvac_systems"],  # Dummy data
            subscription_tier="professional"  # Dummy data
        )
        
        return user
        
    except PyJWTError:
        raise credentials_exception
