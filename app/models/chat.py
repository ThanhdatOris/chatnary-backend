"""
Chat models for AI conversation with documents
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., min_length=1, max_length=1000, description="User question")
    file_ids: Optional[List[str]] = Field(None, description="Specific file IDs to search")
    model: str = Field(default="gemini", pattern="^(openai|gemini)$", description="AI model to use")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of similar chunks to retrieve")

class ChatSource(BaseModel):
    """Source document information"""
    file_id: str
    file_name: str
    chunks: List[Dict[str, Any]]
    chunk_count: int

class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool = True
    answer: str
    sources: List[ChatSource]
    processing_time: float
    model_used: str
    query: str

class ChatHistoryItem(BaseModel):
    """Chat history item"""
    id: str
    query: str
    answer: str
    sources: List[ChatSource]
    model_used: str
    timestamp: float
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    success: bool = True
    data: List[ChatHistoryItem]
    pagination: Dict[str, int]

class ModelStatusResponse(BaseModel):
    """AI model status response"""
    success: bool = True
    models: Dict[str, bool]
    message: str
