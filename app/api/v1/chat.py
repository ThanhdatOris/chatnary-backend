"""
Chat API endpoints
Integrated RAG engine for AI chat with documents
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from app.models.user import User
from app.models.chat import (
    ChatRequest, ChatResponse, ChatHistoryResponse, ModelStatusResponse
)
from app.core.auth import get_current_user
from app.ai.rag_engine import rag_engine
from app.ai.llm_client import llm_client

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chat with documents using RAG
    🔥 Native Python processing - no HTTP overhead!
    """
    try:
        # Process chat request through RAG engine
        response = await rag_engine.chat_with_documents(
            query=request.query,
            user_id=current_user.id,
            file_ids=request.file_ids,
            model_type=request.model,
            top_k=request.top_k
        )
        
        return ChatResponse(
            success=True,
            answer=response.answer,
            sources=response.sources,
            processing_time=response.processing_time,
            model_used=response.model_used,
            query=response.query
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xử lý chat: {str(e)}"
        )

@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = Query(20, ge=1, le=100, description="Number of conversations"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user)
):
    """Get user's chat history"""
    try:
        history = await rag_engine.get_user_chat_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return ChatHistoryResponse(
            success=True,
            data=history,
            pagination={
                "limit": limit,
                "offset": offset,
                "total": len(history)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi lấy lịch sử chat"
        )

@router.get("/chat/models", response_model=ModelStatusResponse)
async def get_model_status():
    """Get available AI model status"""
    try:
        models = llm_client.get_available_models()
        
        available_count = sum(1 for available in models.values() if available)
        
        return ModelStatusResponse(
            success=True,
            models=models,
            message=f"{available_count} model(s) available"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi kiểm tra trạng thái model"
        )

@router.post("/process-document/{file_id}")
async def process_document_for_chat(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Process a specific document for chat"""
    try:
        # Get file metadata
        from app.services.file_service import file_service
        file_metadata = await file_service.get_file_by_id(file_id, current_user.id)
        
        if not file_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File không tồn tại"
            )
        
        # Process document
        file_path = file_service.get_file_path(file_metadata.filename)
        success = await rag_engine.process_file_for_chat(
            file_path, current_user.id, file_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"File '{file_metadata.originalName}' đã được xử lý thành công"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể xử lý file"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xử lý tài liệu: {str(e)}"
        )
