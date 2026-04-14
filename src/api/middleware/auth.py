"""
Authentication Middleware for API Key verification.
"""
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery
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

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

async def get_api_key(
    header_key: str = Security(api_key_header),
    query_key: str = Security(api_key_query),
):
    if not settings.API_KEY_ENABLED:
        return "disabled"
        
    if header_key == settings.API_KEY:
        return header_key
    if query_key == settings.API_KEY:
        return query_key
        
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key"
    )
