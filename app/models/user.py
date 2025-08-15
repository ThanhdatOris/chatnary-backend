"""
User models for authentication and user management
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    fullName: str = Field(..., min_length=1, max_length=100)

class UserCreateRequest(UserBase):
    """User registration request model"""
    password: str = Field(..., min_length=6, max_length=100)

class UserLoginRequest(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

class UserUpdateRequest(BaseModel):
    """User profile update request model"""
    fullName: Optional[str] = Field(None, min_length=1, max_length=100)

class User(UserBase):
    """User response model (without password)"""
    id: str
    role: str = "user"
    isActive: bool = True
    createdAt: datetime
    lastLogin: Optional[datetime] = None

class UserInDB(User):
    """User model for database operations (includes password hash)"""
    password: str

class UserResponse(BaseModel):
    """Standard user response wrapper"""
    success: bool = True
    message: str
    user: User
    token: Optional[str] = None

class LoginResponse(BaseModel):
    """Login response model"""
    success: bool = True
    message: str
    user: User
    token: str

class StandardResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    error: Optional[str] = None
