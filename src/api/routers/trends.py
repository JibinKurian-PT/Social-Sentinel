from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy.future import select # type: ignore
from sqlalchemy import func # type: ignore
from datetime import datetime, timedelta

from src.api.schemas.trends import TrendResponse, TrendAggregated, ComparisonRequest
from src.api.dependencies import DB_Dependency
from src.database.postgres.models import DailyAggregate

router = APIRouter(prefix="/trends", tags=["Trends"])

@router.get("/hourly", response_model=TrendResponse)
async def get_trends_hourly(hours: int = 24, limit: int = 100, offset: int = 0, db: AsyncSession = DB_Dependency):
    """
    Mocked hourly extraction since DailyAggregate is daily. 
    In prod, this queries an hourly_aggregate materialized view.
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Normally this would be group by hour, but we mock with daily
    stmt = select(DailyAggregate).where(DailyAggregate.date >= start_time.date()).order_by(DailyAggregate.date.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    aggregates = result.scalars().all()
    
    if not aggregates:
        # Return sensible mock data if empty DB so dashboard works
        import random
        aggregates = []
        platforms = ["twitter", "youtube"]
        for p in platforms:
            for i in range(24):
                dt = datetime.utcnow().replace(minute=0, second=0, microsecond=0) - timedelta(hours=i)
                aggregates.append(TrendAggregated(
                    date=dt,
                    platform=p,
                    positive_count=random.randint(100, 500),
                    negative_count=random.randint(50, 400),
                    neutral_count=random.randint(200, 800),
                    avg_polarity=random.uniform(-0.5, 0.7)
                ))
    else:
        aggregates = [
            TrendAggregated(
                date=a.date,
                platform=a.platform,
                positive_count=a.positive_count,
                negative_count=a.negative_count,
                neutral_count=a.neutral_count,
                avg_polarity=a.avg_polarity
            ) for a in aggregates
        ]
        
    return TrendResponse(timeframe=f"{hours}h", aggregates=aggregates)

@router.post("/comparison")
async def compare_trends(req: ComparisonRequest, db: AsyncSession = DB_Dependency):
    """Compare sentiment volumes for various keywords. Mock implementation for dashboard."""
    # This would use full text search in Postgres in production
    import random
    results = {}
    for kw in req.keywords:
        results[kw] = {
            "volume": random.randint(1000, 50000),
            "sentiment": {
                "positive": random.randint(10, 60),
                "negative": random.randint(10, 60),
                "neutral": random.randint(10, 40)
            }
        }
    return results
