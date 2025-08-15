"""
Authentication API endpoints
Migrated from Node.js authController.js
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.models.user import (
    UserCreateRequest, UserLoginRequest, UserUpdateRequest,
    User, LoginResponse, UserResponse, StandardResponse
)
from app.core.security import security
from app.core.auth import get_current_user
from app.config.database import get_collection

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreateRequest):
    """
    Register a new user
    Migrated from register function in authController.js
    """
    try:
        # Validate email format
        if not security.validate_email_format(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate password strength
        if not security.validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu phải có ít nhất 6 ký tự"
            )
        
        users_collection = get_collection("users")
        
        # Check if email already exists
        existing_user = await users_collection.find_one(
            {"email": user_data.email.lower()}
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
        
        # Hash password
        hashed_password = security.get_password_hash(user_data.password)
        
        # Create new user
        new_user = {
            "email": user_data.email.lower(),
            "password": hashed_password,
            "fullName": user_data.fullName.strip(),
            "createdAt": datetime.utcnow(),
            "isActive": True,
            "role": "user"
        }
        
        result = await users_collection.insert_one(new_user)
        
        # Create JWT token
        token = security.create_access_token(
            data={
                "userId": str(result.inserted_id),
                "email": new_user["email"],
                "role": new_user["role"]
            }
        )
        
        # Prepare user response (without password)
        user_response = User(
            id=str(result.inserted_id),
            email=new_user["email"],
            fullName=new_user["fullName"],
            role=new_user["role"],
            isActive=new_user["isActive"],
            createdAt=new_user["createdAt"]
        )
        
        return UserResponse(
            success=True,
            message="Đăng ký thành công",
            user=user_response,
            token=token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi đăng ký"
        )

@router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLoginRequest):
    """
    User login
    Migrated from login function in authController.js
    """
    try:
        users_collection = get_collection("users")
        
        # Find user by email
        user = await users_collection.find_one(
            {"email": login_data.email.lower()}
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng"
            )
        
        # Check if account is active
        if not user.get("isActive", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tài khoản đã bị vô hiệu hóa"
            )
        
        # Verify password
        if not security.verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng"
            )
        
        # Create JWT token
        token = security.create_access_token(
            data={
                "userId": str(user["_id"]),
                "email": user["email"],
                "role": user["role"]
            }
        )
        
        # Update last login
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"lastLogin": datetime.utcnow()}}
        )
        
        # Prepare user response (without password)
        user_response = User(
            id=str(user["_id"]),
            email=user["email"],
            fullName=user["fullName"],
            role=user["role"],
            isActive=user["isActive"],
            createdAt=user["createdAt"],
            lastLogin=datetime.utcnow()
        )
        
        return LoginResponse(
            success=True,
            message="Đăng nhập thành công",
            user=user_response,
            token=token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi đăng nhập"
        )

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get user profile
    Migrated from getProfile function in authController.js
    """
    return UserResponse(
        success=True,
        message="Lấy thông tin profile thành công",
        user=current_user
    )

@router.put("/profile", response_model=StandardResponse)
async def update_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile
    Migrated from updateProfile function in authController.js
    """
    try:
        if not update_data.fullName or not update_data.fullName.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đầy đủ không được để trống"
            )
        
        users_collection = get_collection("users")
        
        result = await users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {
                "$set": {
                    "fullName": update_data.fullName.strip(),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        return StandardResponse(
            success=True,
            message="Cập nhật profile thành công"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi cập nhật profile"
        )
