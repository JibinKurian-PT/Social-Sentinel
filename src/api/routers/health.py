from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy import text # type: ignore
from typing import Dict, Any

from src.api.dependencies import DB_Dependency

router = APIRouter(tags=["Monitoring"])

@router.get("/health")
async def health_check(db: AsyncSession = DB_Dependency) -> Dict[str, Any]:
    """Ensure core dependencies are up."""
    db_status = "offline"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "online"
    except Exception:
        pass
        
    return {
        "status": "healthy" if db_status == "online" else "degraded",
        "services": {
            "api": "online",
            "postgres": db_status
        }
    }
