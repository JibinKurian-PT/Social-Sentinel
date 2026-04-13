from fastapi import Header, HTTPException, Depends # type: ignore
from src.config import settings
from src.database.postgres.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
import logging

logger = logging.getLogger(__name__)

async def verify_api_key(api_key: str = Header(None)):
    """Simple API Key validation, if enabled."""
    if settings.API_KEY and api_key != settings.API_KEY:
        logger.warning(f"Invalid API Key attempt. Provided: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return api_key

# Make DB accessible
DB_Dependency = Depends(get_db)
