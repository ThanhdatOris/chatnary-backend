"""
Authentication API endpoints
Migrated from Node.js authController.js
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.models.user import (
    UserCreateRequest, UserLoginRequest, UserUpdateRequest, PasswordChangeRequest,
    User, LoginResponse, UserResponse, StandardResponse
)
from app.core.security import security
from app.core.auth import get_current_user
from app.config.database import get_collection
from app.services.email_service import email_service
import secrets
from datetime import timedelta

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

@router.post("/reset-password", response_model=StandardResponse)
async def reset_password(data: dict):
    """Reset password using token"""
    try:
        token = data.get("token")
        new_password = data.get("newPassword")
        if not token or not new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Thiếu token hoặc mật khẩu mới")

        if not security.validate_password_strength(new_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu mới phải có ít nhất 6 ký tự")

        reset_collection = get_collection("password_resets")
        users_collection = get_collection("users")

        reset_doc = await reset_collection.find_one({"token": token, "used": False})
        if not reset_doc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token không hợp lệ hoặc đã sử dụng")

        if reset_doc.get("expiresAt") and reset_doc["expiresAt"] < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token đã hết hạn")

        hashed_new_password = security.get_password_hash(new_password)
        await users_collection.update_one({"_id": reset_doc["userId"]}, {"$set": {"password": hashed_new_password, "updatedAt": datetime.utcnow()}})
        await reset_collection.update_one({"_id": reset_doc["_id"]}, {"$set": {"used": True, "usedAt": datetime.utcnow()}})

        return StandardResponse(success=True, message="Đặt lại mật khẩu thành công")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lỗi server khi đặt lại mật khẩu")

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

@router.put("/change-password", response_model=StandardResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Change user password
    """
    try:
        # Validate password strength
        if not security.validate_password_strength(password_data.newPassword):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới phải có ít nhất 6 ký tự"
            )
        
        users_collection = get_collection("users")
        
        # Get current user with password
        user = await users_collection.find_one({"_id": ObjectId(current_user.id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        # Verify current password
        if not security.verify_password(password_data.currentPassword, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu hiện tại không đúng"
            )
        
        # Hash new password
        hashed_new_password = security.get_password_hash(password_data.newPassword)
        
        # Update password
        result = await users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {
                "$set": {
                    "password": hashed_new_password,
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
            message="Đổi mật khẩu thành công"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi đổi mật khẩu"
        )

@router.post("/forgot-password", response_model=StandardResponse)
async def forgot_password(email_data: dict):
    email = email_data.get("email", "")
    """
    Send password reset email
    """
    try:
        # Validate email format
        if not security.validate_email_format(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email không hợp lệ"
            )
        
        users_collection = get_collection("users")
        reset_collection = get_collection("password_resets")
        
        # Check if user exists
        user = await users_collection.find_one({"email": email.lower()})
        if not user:
            # Don't reveal if email exists or not for security
            return StandardResponse(
                success=True,
                message="Nếu email tồn tại, bạn sẽ nhận được email hướng dẫn đặt lại mật khẩu"
            )

        # Create reset token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        await reset_collection.insert_one({
            "userId": user["_id"],
            "email": user["email"],
            "token": token,
            "expiresAt": expires_at,
            "used": False,
            "createdAt": datetime.utcnow()
        })

        # Build reset link
        from app.config.settings import settings
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        # Send email (or log)
        subject = "Đặt lại mật khẩu - Chatnary"
        text_body = f"Bạn đã yêu cầu đặt lại mật khẩu. Nhấp vào liên kết sau để đặt lại mật khẩu (có hiệu lực trong 1 giờ):\n{reset_link}\n\nNếu bạn không yêu cầu, hãy bỏ qua email này."
        html_body = f"""
        <p>Xin chào,</p>
        <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Chatnary.</p>
        <p>Nhấp vào liên kết sau để đặt lại mật khẩu (có hiệu lực trong 1 giờ):</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>Nếu bạn không yêu cầu, vui lòng bỏ qua email này.</p>
        """

        email_service.send_email(user["email"], subject, html_body, text_body)

        return StandardResponse(
            success=True,
            message="Nếu email tồn tại, bạn sẽ nhận được email hướng dẫn đặt lại mật khẩu"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi xử lý yêu cầu quên mật khẩu"
        )
