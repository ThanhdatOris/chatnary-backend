"""
Chatnary Backend - Python FastAPI Version
Main application entry point
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import time

from app.config.database import init_db, close_db
from app.config.settings import settings
from app.core.middleware import log_requests
from app.api.v1 import auth, files, search, chat

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Chatnary Python Backend...")
    await init_db()
    print("✅ Database initialized")
    
    # Create uploads directory if not exists
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("vector_stores", exist_ok=True)
    
    yield
    
    # Shutdown
    print("🔄 Shutting down Chatnary Backend...")
    await close_db()
    print("✅ Cleanup completed")

# FastAPI application
app = FastAPI(
    title="Chatnary AI Backend",
    description="Full-stack Python backend with integrated AI capabilities",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend dev server
        "http://localhost:8080",  # Alternative frontend
        settings.FRONTEND_URL or "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(log_requests)

# Static file serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# API Routes
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": time.time(),
        "backend": "Python FastAPI",
        "ai_integrated": True
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Chatnary AI Backend - Python FastAPI 🐍🤖",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Authentication & User Management",
            "File Upload & Management", 
            "Full-text Search (Meilisearch)",
            "AI Chat with Documents (RAG)",
            "Multi-document Support",
            "Vector Similarity Search"
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error responses"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
