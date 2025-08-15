"""
Development server runner for Chatnary Python Backend
"""

import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print("🚀 Starting Chatnary Python Backend...")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print(f"📁 Upload endpoint: http://localhost:{port}/api/upload")
    print(f"🔎 Search endpoint: http://localhost:{port}/api/search")
    print(f"🤖 Chat endpoint: http://localhost:{port}/api/chat")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
