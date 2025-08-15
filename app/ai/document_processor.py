"""
Document processing service
Enhanced and adapted from llm_chatbot_genAI/pre_doc.py
"""

import os
import hashlib
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    from langchain.document_loaders import PyPDFLoader
    from langchain.vectorstores import FAISS
    from langchain.embeddings import HuggingFaceEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.config.settings import settings
from app.config.database import get_collection
from bson import ObjectId

class DocumentProcessor:
    """Enhanced document processor with user context and database integration"""
    
    def __init__(self):
        self.vector_stores_dir = settings.VECTOR_STORE_DIR
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.embeddings = None
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.vector_stores_dir, exist_ok=True)
    
    def _get_embeddings(self):
        """Get or create embeddings model"""
        if self.embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        return self.embeddings
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate unique hash for file"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash[:8]
    
    async def process_document(
        self, 
        file_path: str, 
        user_id: str,
        file_id: str
    ) -> Optional[FAISS]:
        """
        Process a document for a specific user
        Enhanced from process_single_document with user context
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load document
            loader = PyPDFLoader(file_path)
            documents = await asyncio.get_event_loop().run_in_executor(
                None, loader.load
            )
            
            if not documents:
                raise ValueError(f"Could not extract content from: {file_path}")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
                length_function=len,
            )
            
            chunks = text_splitter.split_documents(documents)
            
            # Enhance chunks with metadata
            enhanced_chunks = []
            filename = os.path.basename(file_path)
            
            for i, chunk in enumerate(chunks):
                # Filter out very short chunks
                if len(chunk.page_content.strip()) < 50:
                    continue
                
                # Add enhanced metadata
                chunk.metadata.update({
                    'source_file': filename,
                    'file_id': file_id,
                    'user_id': user_id,
                    'chunk_id': i,
                    'chunk_length': len(chunk.page_content),
                    'processed_at': str(asyncio.get_event_loop().time())
                })
                enhanced_chunks.append(chunk)
            
            if not enhanced_chunks:
                raise ValueError("No valid chunks created from document")
            
            # Create vector store
            embeddings = self._get_embeddings()
            vector_store = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: FAISS.from_documents(enhanced_chunks, embeddings)
            )
            
            # Save vector store
            vector_store_path = self._get_user_vector_store_path(user_id, file_id)
            await asyncio.get_event_loop().run_in_executor(
                None,
                vector_store.save_local,
                vector_store_path
            )
            
            # Update file metadata in database
            await self._update_file_index_status(file_id, user_id, True)
            
            return vector_store
            
        except Exception as e:
            # Update file metadata to indicate indexing failed
            await self._update_file_index_status(file_id, user_id, False)
            raise Exception(f"Error processing document: {str(e)}")
    
    async def load_user_vector_store(
        self, 
        user_id: str, 
        file_id: str
    ) -> Optional[FAISS]:
        """Load vector store for specific user and file"""
        try:
            vector_store_path = self._get_user_vector_store_path(user_id, file_id)
            
            if not os.path.exists(vector_store_path):
                return None
            
            embeddings = self._get_embeddings()
            vector_store = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: FAISS.load_local(
                    vector_store_path, 
                    embeddings, 
                    allow_dangerous_deserialization=True
                )
            )
            
            return vector_store
            
        except Exception as e:
            return None
    
    async def combine_user_vector_stores(
        self, 
        user_id: str, 
        file_ids: List[str]
    ) -> Optional[FAISS]:
        """Combine multiple vector stores for a user"""
        try:
            combined_store = None
            
            for file_id in file_ids:
                store = await self.load_user_vector_store(user_id, file_id)
                if store:
                    if combined_store is None:
                        combined_store = store
                    else:
                        combined_store.merge_from(store)
            
            return combined_store
            
        except Exception as e:
            return None
    
    async def get_user_processed_files(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of processed files for a user"""
        try:
            files_collection = get_collection("files")
            cursor = files_collection.find({
                "userId": ObjectId(user_id),
                "indexed": True
            })
            
            files = await cursor.to_list(length=None)
            
            processed_files = []
            for file_doc in files:
                vector_store_path = self._get_user_vector_store_path(
                    user_id, file_doc["id"]
                )
                
                # Verify vector store actually exists
                if os.path.exists(vector_store_path):
                    processed_files.append({
                        "id": file_doc["id"],
                        "originalName": file_doc["originalName"],
                        "filename": file_doc["filename"],
                        "uploadTime": file_doc["uploadTime"],
                        "vector_store_path": vector_store_path
                    })
            
            return processed_files
            
        except Exception as e:
            return []
    
    def _get_user_vector_store_path(self, user_id: str, file_id: str) -> str:
        """Get vector store path for user and file"""
        return os.path.join(
            self.vector_stores_dir,
            f"user_{user_id}",
            f"file_{file_id}"
        )
    
    async def _update_file_index_status(
        self, 
        file_id: str, 
        user_id: str, 
        indexed: bool
    ):
        """Update file indexing status in database"""
        try:
            files_collection = get_collection("files")
            await files_collection.update_one(
                {
                    "id": file_id,
                    "userId": ObjectId(user_id)
                },
                {
                    "$set": {
                        "indexed": indexed,
                        "indexedAt": asyncio.get_event_loop().time() if indexed else None
                    }
                }
            )
        except Exception as e:
            # Log error but don't raise - this is not critical
            print(f"Warning: Could not update file index status: {e}")
    
    async def delete_user_vector_store(self, user_id: str, file_id: str) -> bool:
        """Delete vector store for specific file"""
        try:
            vector_store_path = self._get_user_vector_store_path(user_id, file_id)
            
            if os.path.exists(vector_store_path):
                import shutil
                shutil.rmtree(vector_store_path)
                return True
            
            return False
            
        except Exception as e:
            return False

# Global document processor instance
document_processor = DocumentProcessor()
