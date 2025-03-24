from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

from app.db.models.user import UserRole

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[str] = "estimator"

    @validator("role")
    def validate_role(cls, v):
        if v not in [role.value for role in UserRole]:
            raise ValueError(f"Invalid role. Must be one of: {', '.join([role.value for role in UserRole])}")
        return v

class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserResponse(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
