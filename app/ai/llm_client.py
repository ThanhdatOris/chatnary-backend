"""
LLM client for various AI providers
Enhanced and adapted from llm_chatbot_genAI/llm_rag.py
"""

import os
from typing import Optional, Dict, Any
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

from app.config.settings import settings

class LLMClient:
    """Client for interacting with various LLM providers"""
    
    def __init__(self):
        self._openai_client = None
        self._gemini_client = None
    
    def get_openai_client(self):
        """Get or create OpenAI client"""
        if self._openai_client is None:
            api_key = settings.OPENAI_API_KEY
            if not api_key or api_key == 'your_openai_api_key_here':
                raise ValueError("OpenAI API key not configured")
            
            self._openai_client = OpenAI(
                temperature=0.7,
                openai_api_key=api_key,
                max_tokens=500
            )
        
        return self._openai_client
    
    def get_gemini_client(self):
        """Get or create Gemini client"""
        if self._gemini_client is None:
            if ChatGoogleGenerativeAI is None:
                raise ImportError("langchain-google-genai not installed")
            
            api_key = settings.GEMINI_API_KEY
            if not api_key or api_key == 'your_gemini_api_key_here':
                raise ValueError("Gemini API key not configured")
            
            # Try Gemini models in order of preference
            gemini_models = [
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash", 
                "gemini-1.5-pro",
                "gemini-pro"
            ]
            
            last_error = None
            for model_name in gemini_models:
                try:
                    self._gemini_client = ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=api_key,
                        temperature=0.7,
                        convert_system_message_to_human=True
                    )
                    break
                except Exception as e:
                    last_error = e
                    continue
            
            if self._gemini_client is None:
                raise ValueError(f"Could not initialize any Gemini model. Last error: {last_error}")
        
        return self._gemini_client
    
    def get_client(self, model_type: str = "gemini"):
        """Get LLM client by type"""
        if model_type == "openai":
            return self.get_openai_client()
        elif model_type == "gemini":
            return self.get_gemini_client()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def create_qa_chain(self, vector_store, model_type: str = "gemini"):
        """
        Create QA chain with vector store
        Enhanced from create_qa_chain function in llm_rag.py
        """
        llm = self.get_client(model_type)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 10}),
            return_source_documents=True
        )
        
        return qa_chain
    
    def get_available_models(self) -> Dict[str, bool]:
        """Check which models are available"""
        models = {
            "openai": False,
            "gemini": False
        }
        
        # Check OpenAI
        try:
            api_key = settings.OPENAI_API_KEY
            if api_key and api_key != 'your_openai_api_key_here':
                models["openai"] = True
        except:
            pass
        
        # Check Gemini
        try:
            api_key = settings.GEMINI_API_KEY
            if api_key and api_key != 'your_gemini_api_key_here' and ChatGoogleGenerativeAI:
                models["gemini"] = True
        except:
            pass
        
        return models

# Global LLM client instance
llm_client = LLMClient()
