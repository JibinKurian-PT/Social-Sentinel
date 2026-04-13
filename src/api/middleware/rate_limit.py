"""
Rate Limiting Middleware (in-memory for simple limits).
For multi-replica production environments, use Redis.
"""
import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # dict mapping IP -> list of timestamps
        self.request_records = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        # Only rate limit API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean up old records for this IP
        self.request_records[client_ip] = [
            ts for ts in self.request_records[client_ip] 
            if now - ts < self.window_seconds
        ]
        
        # Check limit
        if len(self.request_records[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests: Rate limit exceeded"}
            )
            
        # Record this request
        self.request_records[client_ip].append(now)
        
        return await call_next(request)
