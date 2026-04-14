from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy.future import select # type: ignore

from src.api.dependencies import DB_Dependency
from src.database.postgres.models import Topic

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.get("")
async def get_active_topics(limit: int = 10, db: AsyncSession = DB_Dependency):
    """Get currently active topics extracted by LDA."""
    stmt = select(Topic).order_by(Topic.volume.desc()).limit(limit)
    result = await db.execute(stmt)
    topics = result.scalars().all()
    
    if not topics:
        # Fallback mock for dashboard start
        return [
            {
                "topic_id": 1, 
                "name": "Artificial Intelligence", 
                "keywords": ["ai", "model", "gpt"], 
                "weights": [0.8, 0.6, 0.4],
                "volume": 14500, 
                "avg_sentiment": 0.4
            },
            {
                "topic_id": 2, 
                "name": "Customer Support", 
                "keywords": ["help", "fix", "ticket"], 
                "weights": [0.9, 0.7, 0.5],
                "volume": 8200, 
                "avg_sentiment": -0.6
            },
            {
                "topic_id": 3, 
                "name": "Pricing/Sales", 
                "keywords": ["price", "expensive", "sale"], 
                "weights": [0.75, 0.5, 0.3],
                "volume": 5300, 
                "avg_sentiment": -0.2
            }
        ]
        
    return [
        {
            "topic_id": t.id,
            "name": t.name,
            "keywords": t.keywords if isinstance(t.keywords, list) else [],
            "weights": [0.5] * len(t.keywords) if isinstance(t.keywords, list) else [], # Fallback weights for stored topics
            "volume": t.volume,
            "avg_sentiment": t.avg_sentiment,
            "last_updated": t.last_updated
        } for t in topics
    ]
