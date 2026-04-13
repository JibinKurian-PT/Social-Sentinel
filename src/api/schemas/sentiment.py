from pydantic import BaseModel, Field # type: ignore
from typing import List, Optional
from datetime import datetime

class RequestMetrics(BaseModel):
    processing_time_ms: float

class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)

class BatchSentimentRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)

class SentimentResultResponse(BaseModel):
    text: str
    label: str
    polarity: float
    confidence: float
    model_used: str

class DBHistoryResponse(BaseModel):
    id: int
    text: str
    platform: str
    created_at: datetime
    sentiment_label: str
    polarity: float
    confidence: float

class SentimentBatchResponse(BaseModel):
    results: List[SentimentResultResponse]
    metrics: RequestMetrics
