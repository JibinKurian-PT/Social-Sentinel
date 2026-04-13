from pydantic import BaseModel # type: ignore
from typing import Optional, List

class GeoPoint(BaseModel):
    lat: float
    lon: float

class GeoSentimentResponse(BaseModel):
    location: str
    count: int
    avg_polarity: float
    dominant_sentiment: str
