"""
User management API endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, EmailStr
from sqlalchemy.orm import Session

from ...core.security import get_password_hash, get_current_active_superuser, get_current_user
from ...db import models
from ...db.session import get_db
from ...schemas.user import User, UserCreate, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users (superuser only).
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    # Check if user already exists
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_data = user_in.dict(exclude={"password"})
    user_data["hashed_password"] = get_password_hash(user_in.password)
    user = models.User(**user_data)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/me", response_model=User)
def read_user_me(
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    full_name: str = Body(None),
    company_name: str = Body(None),
    email: EmailStr = Body(None),
    password: str = Body(None),
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(
        full_name=full_name or current_user.full_name,
        company_name=company_name or current_user.company_name,
        email=email or current_user.email,
        password=password,
    )
    
    user_data = user_in.dict(exclude_unset=True)
    
    if user_data.get("password"):
        user_data["hashed_password"] = get_password_hash(user_data["password"])
        del user_data["password"]
    
    # Update user
    for field in user_data:
        setattr(current_user, field, user_data[field])
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: UUID4,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only allow superusers or the user themselves to view their own data
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: UUID4,
    user_in: UserUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user (superuser only).
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    user_data = user_in.dict(exclude_unset=True)
    
    if user_data.get("password"):
        user_data["hashed_password"] = get_password_hash(user_data["password"])
        del user_data["password"]
    
    for field in user_data:
        setattr(user, field, user_data[field])
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: UUID4,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete a user (superuser only).
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return user
