"""
File management API endpoints
Migrated from Node.js fileController.js and fileDetailController.js
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse
from typing import Optional
import os
import aiofiles
from app.models.file import (
    FileUploadResponse, FileListResponse, FileDetailResponse, 
    FileStatsResponse, FileMetadata
)
from app.models.user import StandardResponse, User
from app.core.auth import get_current_user, get_current_user_optional
from app.services.file_service import file_service
from app.config.settings import settings

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file
    Migrated from uploadFile function in fileController.js
    """
    try:
        # Validate file type
        if not file_service.validate_file_type(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ cho phép upload file PDF, DOCX, DOC, TXT, MD"
            )
        
        # Validate file size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File quá lớn. Giới hạn {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        
        # Generate unique filename
        unique_filename = file_service.generate_unique_filename(file.filename)
        file_path = file_service.get_file_path(unique_filename)
        
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Prepare file metadata
        file_metadata_data = {
            "originalName": file.filename,
            "filename": unique_filename,
            "size": file.size,
            "mimetype": file.content_type,
            "path": file_path,
            "userId": current_user.id,
            "userEmail": current_user.email
        }
        
        # Save metadata to database
        saved_metadata = await file_service.save_file_metadata(file_metadata_data)
        
        # TODO: Index file content in background (will be implemented in search service)
        
        return FileUploadResponse(
            success=True,
            message="File đã được upload thành công",
            file=saved_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if metadata save failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi upload file"
        )

@router.get("/files", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sortBy: str = Query("uploadTime", description="Sort field"),
    sortOrder: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_user)
):
    """
    List user's files with pagination
    Migrated from listFiles function in fileDetailController.js
    """
    try:
        result = await file_service.get_user_files(
            user_id=current_user.id,
            page=page,
            limit=limit,
            sort_by=sortBy,
            sort_order=sortOrder
        )
        
        return FileListResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi lấy danh sách file"
        )

@router.get("/files/{file_id}", response_model=FileDetailResponse)
async def get_file_detail(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get file detail by ID
    Migrated from getFileDetail function in fileDetailController.js
    """
    try:
        file_metadata = await file_service.get_file_by_id(file_id, current_user.id)
        
        if not file_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File không tồn tại"
            )
        
        return FileDetailResponse(
            success=True,
            file=file_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi lấy thông tin file"
        )

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download file by ID
    Migrated from downloadFile function in fileDetailController.js
    """
    try:
        file_metadata = await file_service.get_file_by_id(file_id, current_user.id)
        
        if not file_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File không tồn tại"
            )
        
        file_path = file_service.get_file_path(file_metadata.filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File vật lý không tồn tại"
            )
        
        return FileResponse(
            path=file_path,
            filename=file_metadata.originalName,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi download file"
        )

@router.delete("/files/{file_id}", response_model=StandardResponse)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete file by ID
    Migrated from deleteFile function in fileDetailController.js
    """
    try:
        success = await file_service.delete_file(file_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File không tồn tại"
            )
        
        return StandardResponse(
            success=True,
            message="File đã được xóa thành công"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi xóa file"
        )

@router.get("/stats", response_model=FileStatsResponse)
async def get_file_stats(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get file statistics
    Public endpoint with optional authentication
    """
    try:
        user_id = current_user.id if current_user else None
        stats = await file_service.get_file_stats(user_id)
        
        return FileStatsResponse(
            success=True,
            stats=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi server khi lấy thống kê file"
        )
