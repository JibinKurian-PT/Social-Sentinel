import asyncio
from celery import shared_task # type: ignore
from typing import List
import logging
from src.collectors.twitter_collector import TwitterCollector
from src.collectors.youtube_collector import YouTubeCollector
from src.database.mongo.connection import get_mongo_db

logger = logging.getLogger(__name__)

# Default keywords to monitor if none provided
DEFAULT_KEYWORDS = ["artificial intelligence", "tech", "cloud computing", "crypto"]

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def schedule_twitter_collection(self, keywords: List[str] = None):
    """Wrapper to run async collection inside synchronous Celery worker."""
    if keywords is None:
        keywords = DEFAULT_KEYWORDS
        
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(_async_twitter_collection(keywords))
    except Exception as exc:
        logger.error(f"Error in schedule_twitter_collection: {exc}")
        # Exponential backoff retry
        self.retry(exc=exc, countdown=2 ** self.request.retries * 60)

async def _async_twitter_collection(keywords: List[str]):
    collector = TwitterCollector()
    db = await get_mongo_db()
    
    total_saved = 0
    for keyword in keywords:
        # Collect and save per keyword
        data = await collector.collect(keyword, max_results=100)
        if data:
            success = await collector.save_to_mongo(db, data, "raw_twitter")
            if success:
                total_saved += len(data)
                
    return {"status": "success", "platform": "twitter", "count": total_saved}


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def schedule_youtube_collection(self, keywords: List[str] = None):
    """Wrapper to run async collection inside synchronous Celery worker."""
    if keywords is None:
        keywords = DEFAULT_KEYWORDS
        
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(_async_youtube_collection(keywords))
    except Exception as exc:
        logger.error(f"Error in schedule_youtube_collection: {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries * 120)


async def _async_youtube_collection(keywords: List[str]):
    collector = YouTubeCollector()
    db = await get_mongo_db()
    
    total_saved = 0
    for keyword in keywords:
        data = await collector.collect(keyword, max_results=50) # Lower to respect API quota
        if data:
            success = await collector.save_to_mongo(db, data, "raw_youtube")
            if success:
                total_saved += len(data)
                
    return {"status": "success", "platform": "youtube", "count": total_saved}

# Beat scheduler aliases
@shared_task
def scheduled_twitter_collection():
    schedule_twitter_collection.delay()
    
@shared_task
def scheduled_youtube_collection():
    schedule_youtube_collection.delay()
