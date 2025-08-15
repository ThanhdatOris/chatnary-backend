"""
Authentication dependencies and utilities
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.security import security
from app.config.database import get_collection
from app.models.user import User
from bson import ObjectId

# HTTP Bearer token scheme
security_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> User:
    """
    Get current authenticated user from JWT token
    Equivalent to authenticateToken middleware in Node.js version
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = security.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("userId")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        users_collection = get_collection("users")
        user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if user_data is None:
            raise credentials_exception
        
        # Check if user is active
        if not user_data.get("isActive", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        # Convert to User model
        user = User(
            id=str(user_data["_id"]),
            email=user_data["email"],
            fullName=user_data["fullName"],
            role=user_data.get("role", "user"),
            isActive=user_data.get("isActive", True),
            createdAt=user_data["createdAt"],
            lastLogin=user_data.get("lastLogin")
        )
        
        return user
        
    except Exception as e:
        raise credentials_exception

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user optionally (for endpoints that work with or without auth)
    Equivalent to optionalAuth middleware in Node.js version
    """
    if credentials is None:
        return None
    
    try:
        # Create a new HTTPAuthorizationCredentials for the required function
        required_credentials = HTTPAuthorizationCredentials(
            scheme=credentials.scheme,
            credentials=credentials.credentials
        )
        return await get_current_user(required_credentials)
    except HTTPException:
        return None

def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
