"""
Schema definitions for user management.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "company_name": "ABC Construction",
                "password": "strongpassword123"
            }
        }


class UserUpdate(BaseModel):
    """Schema for user updates."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    password: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "John Smith",
                "company_name": "Smith Construction LLC"
            }
        }


class UserInDBBase(UserBase):
    """User schema with DB fields."""
    id: UUID
    
    class Config:
        orm_mode = True


class User(UserInDBBase):
    """User response schema."""
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "email": "user@example.com",
                "full_name": "John Doe",
                "company_name": "ABC Construction",
                "is_active": True,
                "is_superuser": False
            }
        }


class UserInDB(UserInDBBase):
    """User schema with password hash."""
    hashed_password: str


class Token(BaseModel):
    """Authentication token schema."""
    access_token: str
    token_type: str
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123"
            }
        }
