"""
Authentication Middleware for API Key verification.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.config import settings

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Exclude paths that do not require auth (like docs, health checks)
        self.excluded_paths = {
            "/api/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/ws" # Websockets handle auth natively or skip
        }

    async def dispatch(self, request: Request, call_next):
        # If API key is disabled globally or path is excluded, pass through
        if not settings.API_KEY_ENABLED or any(request.url.path.startswith(p) for p in self.excluded_paths):
            return await call_next(request)

        # Check X-API-Key header OR api_key query parameter
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            api_key = request.query_params.get("api_key")
            
        if not api_key or api_key != settings.API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized: Invalid or missing X-API-Key header or api_key query parameter"}
            )
            
        return await call_next(request)
