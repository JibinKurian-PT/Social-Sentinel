import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker # type: ignore
from sqlalchemy.orm import declarative_base # type: ignore
from src.config import settings

logger = logging.getLogger(__name__)

# ── Database URL Setup ───────────────────────────────────────────────
# Always use the setting from config.py which handles interpolation fixes
DATABASE_URL = settings.DATABASE_URL

try:
    # ── Power-Tuned Engine for Production ─────────────────────────────
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        # Performance tuning: 10 fixed connections, up to 20 burstable
        pool_size=10,
        max_overflow=20,
        # Integrity checks
        pool_pre_ping=True,
        # Timeout settings to prevent hanging connections
        pool_recycle=3600,
        pool_timeout=30
    )
    
    async_session_factory = async_sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False,
        autoflush=False
    )
except Exception as e:
    logger.critical(f"FATAL: Database engine initialization failed: {e}")
    engine = None
    async_session_factory = None

Base = declarative_base()

async def get_db() -> AsyncSession: # type: ignore
    """
    Dependency generator for FastAPI routes to inject DB sessions.
    Handles automatic rollback on failure and ensures closure.
    """
    if async_session_factory is None:
        logger.error("Attempted get_db while factory was uninitialized.")
        raise ConnectionError("Database factory not initialized")
        
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session operation failed, rolling back: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
