from pydantic import BaseModel # type: ignore
from typing import List, Dict, Any
from datetime import datetime

class TrendAggregated(BaseModel):
    date: datetime
    platform: str
    positive_count: int
    negative_count: int
    neutral_count: int
    avg_polarity: float

class TrendResponse(BaseModel):
    timeframe: str
    aggregates: List[TrendAggregated]

class ComparisonRequest(BaseModel):
    keywords: List[str]
    days: int = 7
