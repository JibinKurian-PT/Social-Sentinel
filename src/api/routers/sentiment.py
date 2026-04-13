import time
from fastapi import APIRouter, HTTPException, Depends # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy.future import select # type: ignore
from typing import List

from src.api.schemas.sentiment import (
    SentimentAnalysisRequest, 
    BatchSentimentRequest, 
    SentimentResultResponse, 
    SentimentBatchResponse,
    RequestMetrics,
    DBHistoryResponse
)
from src.api.dependencies import DB_Dependency
from src.nlp.sentiment.ensemble_analyzer import EnsembleAnalyzer
from src.database.postgres.models import SentimentResult, Tweet

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])
analyzer = EnsembleAnalyzer()

@router.post("/analyze", response_model=SentimentResultResponse)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """Analyze sentiment of a single text string."""
    try:
        result = analyzer.analyze(request.text)
        return SentimentResultResponse(
            text=request.text,
            label=result["label"],
            polarity=result["polarity"],
            confidence=result["confidence"],
            model_used=result["model_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=SentimentBatchResponse)
async def analyze_sentiment_batch(request: BatchSentimentRequest):
    """Analyze sentiment for a list of text strings."""
    start_time = time.time()
    try:
        results = analyzer.analyze_batch(request.texts)
        
        response_items = []
        for text, res in zip(request.texts, results):
            response_items.append(SentimentResultResponse(
                text=text,
                label=res["label"],
                polarity=res["polarity"],
                confidence=res["confidence"],
                model_used=res["model_used"]
            ))
            
        metrics = RequestMetrics(processing_time_ms=(time.time() - start_time) * 1000)
        return SentimentBatchResponse(results=response_items, metrics=metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[DBHistoryResponse])
async def get_sentiment_history(limit: int = 50, db: AsyncSession = DB_Dependency):
    """Fetch recently analyzed posts from the database."""
    stmt = select(Tweet, SentimentResult).join(SentimentResult, Tweet.id == SentimentResult.tweet_id).order_by(Tweet.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        DBHistoryResponse(
            id=t.id,
            text=t.text,
            platform=t.platform,
            created_at=t.created_at,
            sentiment_label=s.label,
            polarity=s.polarity,
            confidence=s.confidence
        )
        for t, s in rows
    ]

@router.get("/stats")
async def get_sentiment_stats(db: AsyncSession = DB_Dependency):
    """Get aggregate sentiment statistics."""
    from sqlalchemy import func
    stmt = select(SentimentResult.label, func.count(SentimentResult.id)).group_by(SentimentResult.label)
    result = await db.execute(stmt)
    stats = {label: count for label, count in result.all()}
    return {"stats": stats, "total": sum(stats.values()) if stats else 0}
