"""
Custom middleware for the application
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """
    Log all requests with processing time
    Equivalent to requestLogger middleware in Node.js version
    """
    start_time = time.time()
    
    # Log request start
    logger.info(f"🔄 {request.method} {request.url.path} - Started")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request completion
    logger.info(
        f"✅ {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic rate limiting middleware
    """
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: calls for ip, calls in self.clients.items()
            if any(call_time > current_time - 60 for call_time in calls)
        }
        
        # Check rate limit
        if client_ip in self.clients:
            recent_calls = [
                call_time for call_time in self.clients[client_ip]
                if call_time > current_time - 60
            ]
            if len(recent_calls) >= self.calls_per_minute:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "message": "Rate limit exceeded. Please try again later."
                    }
                )
        else:
            self.clients[client_ip] = []
        
        # Add current call
        self.clients[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
