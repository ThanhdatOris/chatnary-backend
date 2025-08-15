"""
File models for upload and management
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FileUploadResponse(BaseModel):
    """File upload response model"""
    success: bool = True
    message: str
    file: "FileMetadata"

class FileMetadata(BaseModel):
    """File metadata model"""
    id: str
    originalName: str
    filename: str
    size: int
    mimetype: str
    uploadTime: datetime
    userId: str
    userEmail: str
    indexed: bool = False
    downloadUrl: Optional[str] = None
    previewUrl: Optional[str] = None

class FileListResponse(BaseModel):
    """File list response model"""
    success: bool = True
    data: "FileListData"

class FileListData(BaseModel):
    """File list data model"""
    files: List[FileMetadata]
    pagination: "PaginationInfo"

class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    limit: int
    total: int
    totalPages: int

class FileDetailResponse(BaseModel):
    """File detail response model"""
    success: bool = True
    file: "FileDetail"

class FileDetail(FileMetadata):
    """Extended file detail model"""
    searchData: Optional[dict] = None

class FileStatsResponse(BaseModel):
    """File statistics response model"""
    success: bool = True
    stats: "FileStats"

class FileStats(BaseModel):
    """File statistics model"""
    totalFiles: int
    indexedFiles: int
    recentFiles: int
    fileTypes: List["FileTypeStats"]

class FileTypeStats(BaseModel):
    """File type statistics"""
    extension: str
    count: int
    totalSize: str

# Update forward references
FileUploadResponse.model_rebuild()
FileListResponse.model_rebuild()
FileDetailResponse.model_rebuild()
FileStatsResponse.model_rebuild()
