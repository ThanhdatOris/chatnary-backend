"""
RAG Engine for chat with documents
Core AI processing engine integrated from llm_chatbot_genAI
"""

import time
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from app.ai.document_processor import document_processor
from app.ai.llm_client import llm_client
from app.config.database import get_collection
from bson import ObjectId

@dataclass
class RAGResponse:
    """Response from RAG engine"""
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float
    model_used: str
    query: str

class RAGEngine:
    """
    Core RAG engine for chat with documents
    Integrated and enhanced from llm_chatbot_genAI
    """
    
    def __init__(self):
        self.doc_processor = document_processor
        self.llm = llm_client
    
    async def chat_with_documents(
        self,
        query: str,
        user_id: str,
        file_ids: Optional[List[str]] = None,
        model_type: str = "gemini",
        top_k: int = 5
    ) -> RAGResponse:
        """
        Main chat function - process query against user's documents
        """
        start_time = time.time()
        
        try:
            # Get user's files to search
            if file_ids:
                # Specific files requested
                search_files = file_ids
            else:
                # Search all user's processed files
                processed_files = await self.doc_processor.get_user_processed_files(user_id)
                search_files = [f["id"] for f in processed_files]
            
            if not search_files:
                return RAGResponse(
                    answer="Bạn chưa có tài liệu nào được xử lý. Hãy upload và xử lý file PDF trước.",
                    sources=[],
                    processing_time=time.time() - start_time,
                    model_used=model_type,
                    query=query
                )
            
            # Load and combine vector stores
            vector_store = await self.doc_processor.combine_user_vector_stores(
                user_id, search_files
            )
            
            if not vector_store:
                return RAGResponse(
                    answer="Không thể tải vector store cho tài liệu của bạn. Vui lòng thử lại sau.",
                    sources=[],
                    processing_time=time.time() - start_time,
                    model_used=model_type,
                    query=query
                )
            
            # Create QA chain
            qa_chain = self.llm.create_qa_chain(vector_store, model_type)
            
            # Execute query
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: qa_chain.invoke({"query": query})
            )
            
            # Process response
            answer = result.get('result', 'Không tìm thấy thông tin phù hợp.')
            source_docs = result.get('source_documents', [])
            
            # Format sources
            sources = await self._format_sources(source_docs, user_id)
            
            # Log conversation
            await self._log_conversation(user_id, query, answer, sources, model_type)
            
            processing_time = time.time() - start_time
            
            return RAGResponse(
                answer=answer,
                sources=sources,
                processing_time=processing_time,
                model_used=model_type,
                query=query
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Có lỗi xảy ra khi xử lý câu hỏi: {str(e)}"
            
            return RAGResponse(
                answer=error_message,
                sources=[],
                processing_time=processing_time,
                model_used=model_type,
                query=query
            )
    
    async def _format_sources(
        self, 
        source_docs: List[Any], 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Format source documents for response"""
        sources = []
        
        # Group sources by file
        sources_by_file = {}
        for doc in source_docs[:10]:  # Limit to top 10 sources
            file_id = doc.metadata.get('file_id', 'Unknown')
            if file_id not in sources_by_file:
                sources_by_file[file_id] = []
            sources_by_file[file_id].append(doc)
        
        # Get file metadata for each source file
        files_collection = get_collection("files")
        
        for file_id, docs in sources_by_file.items():
            try:
                # Get file info from database
                file_info = await files_collection.find_one({
                    "id": file_id,
                    "userId": ObjectId(user_id)
                })
                
                file_name = file_info["originalName"] if file_info else "Unknown File"
                
                # Process documents for this file
                file_sources = []
                for doc in docs[:3]:  # Max 3 chunks per file
                    page_num = doc.metadata.get('page', 'N/A')
                    chunk_content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                    
                    file_sources.append({
                        "page": page_num,
                        "content": chunk_content,
                        "chunk_id": doc.metadata.get('chunk_id', 0)
                    })
                
                sources.append({
                    "file_id": file_id,
                    "file_name": file_name,
                    "chunks": file_sources,
                    "chunk_count": len(docs)
                })
                
            except Exception as e:
                # If file info retrieval fails, still include the source
                sources.append({
                    "file_id": file_id,
                    "file_name": "Unknown File",
                    "chunks": [{
                        "page": "N/A",
                        "content": docs[0].page_content[:300] + "..." if docs else "",
                        "chunk_id": 0
                    }],
                    "chunk_count": len(docs)
                })
        
        return sources
    
    async def _log_conversation(
        self,
        user_id: str,
        query: str,
        answer: str,
        sources: List[Dict[str, Any]],
        model_type: str
    ):
        """Log conversation to database for history"""
        try:
            chat_collection = get_collection("chat_history")
            
            conversation = {
                "userId": ObjectId(user_id),
                "query": query,
                "answer": answer,
                "sources": sources,
                "model_used": model_type,
                "timestamp": time.time(),
                "createdAt": asyncio.get_event_loop().time()
            }
            
            await chat_collection.insert_one(conversation)
            
        except Exception as e:
            # Log error but don't raise - this is not critical for user experience
            print(f"Warning: Could not log conversation: {e}")
    
    async def get_user_chat_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get chat history for user"""
        try:
            chat_collection = get_collection("chat_history")
            
            cursor = chat_collection.find(
                {"userId": ObjectId(user_id)}
            ).sort("timestamp", -1).skip(offset).limit(limit)
            
            history = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON response
            for chat in history:
                chat["_id"] = str(chat["_id"])
                chat["userId"] = str(chat["userId"])
            
            return history
            
        except Exception as e:
            return []
    
    async def process_file_for_chat(
        self,
        file_path: str,
        user_id: str,
        file_id: str
    ) -> bool:
        """Process a file for chat (wrapper around document processor)"""
        try:
            vector_store = await self.doc_processor.process_document(
                file_path, user_id, file_id
            )
            return vector_store is not None
        except Exception as e:
            return False

# Global RAG engine instance  
rag_engine = RAGEngine()
