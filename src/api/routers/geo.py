from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy.future import select # type: ignore
from sqlalchemy import func # type: ignore
from typing import List, Dict, Tuple
from geopy.geocoders import Nominatim # type: ignore
from geopy.exc import GeocoderTimedOut # type: ignore
import time
import logging

from src.api.schemas.geo import GeoSentimentResponse
from src.api.dependencies import DB_Dependency
from src.database.postgres.models import Tweet, SentimentResult

router = APIRouter(prefix="/geo", tags=["Geo Maps"])
logger = logging.getLogger(__name__)

# Simple in-memory cache for geocoder to avoid API limits (1 sec delay per request is typical for Nominatim)
# In production with multiple workers, this should be in Redis.
GEO_CACHE: Dict[str, Tuple[float, float]] = {
    # Pre-populate common locations to speed up loading
    "New York, US": (40.7128, -74.0060),
    "San Francisco, US": (37.7749, -122.4194),
    "London, UK": (51.5074, -0.1278),
    "Berlin, DE": (52.5200, 13.4050),
    "Tokyo, JP": (35.6762, 139.6503),
    "Sydney, AU": (-33.8688, 151.2093),
    "Toronto, CA": (43.6532, -79.3832),
    "Singapore, SG": (1.3521, 103.8198),
    "Mumbai, IN": (19.0760, 72.8777),
    "Bangalore, IN": (12.9716, 77.5946),
    "Paris, FR": (48.8566, 2.3522),
    "Amsterdam, NL": (52.3676, 4.9041),
}

# The user-agent is strictly required by Nominatim
geolocator = Nominatim(user_agent="social_sentiment_system_v2")

async def get_coordinates(location_name: str) -> Tuple[float, float]:
    """Geocode a string to lat/lon with caching."""
    if not location_name or not location_name.strip():
        return (0.0, 0.0)
        
    loc = location_name.strip()
    if loc in GEO_CACHE:
        return GEO_CACHE[loc]
        
    try:
        # Nominatim asks for 1 request per second
        time.sleep(1.1) 
        location = geolocator.geocode(loc, timeout=5)
        if location:
            GEO_CACHE[loc] = (location.latitude, location.longitude)
            return GEO_CACHE[loc]
    except GeocoderTimedOut:
        logger.warning(f"Geocoding timed out for {loc}")
    except Exception as e:
        logger.warning(f"Geocoding failed for {loc}: {e}")
        
    # Return 0.0 if failed
    return (0.0, 0.0)

@router.get("", response_model=List[GeoSentimentResponse])
async def get_geo_sentiment(limit: int = 100, db: AsyncSession = DB_Dependency):
    """Retrieve actual database sentiment grouped by detected locations and geocode them."""
    
    # Query tweets joined with their sentiment to aggregate by location
    stmt = (
        select(
            Tweet.location,
            func.count(Tweet.id).label("count"),
            func.avg(SentimentResult.polarity).label("avg_polarity")
        )
        .join(SentimentResult, Tweet.id == SentimentResult.tweet_id)
        .where(Tweet.location.is_not(None))
        .where(Tweet.location != "")
        .group_by(Tweet.location)
        .order_by(func.count(Tweet.id).desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    responses = []
    
    for row in rows:
        loc_name, count, avg_pol = row
        lat, lon = await get_coordinates(loc_name)
        
        # Skip if geocoding totally failed (0,0 is usually the ocean south of Ghana)
        if lat == 0.0 and lon == 0.0:
            continue
            
        pol = float(avg_pol) if avg_pol is not None else 0.0
        dom = "positive" if pol > 0.05 else "negative" if pol < -0.05 else "neutral"
        
        # We extend the response if needed, but rely on Dashboard geocoding handling.
        # Note: the schema in schemas/geo might not have lat/lon fields yet, 
        # but the dashboard 04_GeoMap.py doesn't strictly validate Pydantic output, 
        # it just uses the JSON. However, let's keep it safe.
        responses.append({
            "location": loc_name,
            "count": count,
            "avg_polarity": pol,
            "dominant_sentiment": dom,
            "latitude": lat,
            "longitude": lon
        })
        
    return responses
