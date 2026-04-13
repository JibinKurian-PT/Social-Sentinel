import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Abstract base class for all external API data collectors."""
    
    @abstractmethod
    async def collect(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Collect data for a given query."""
        pass
        
    async def save_to_mongo(self, db, data: List[Dict[str, Any]], collection_name: str) -> bool:
        """Save collected raw data to MongoDB using Motor async operations."""
        if not data:
            return False
            
        collection = db[collection_name]
        try:
            # We use insert_many but we ignore duplicate key errors (platform_id) using ordered=False
            from pymongo.errors import BulkWriteError
            try:
                await collection.insert_many(data, ordered=False)
                logger.info(f"Saved {len(data)} items to MongoDB collection: {collection_name}")
                return True
            except BulkWriteError as bwe:
                # Some inserts failed (likely duplicates due to unique platform_id index), but others succeeded
                werrors = bwe.details.get('writeErrors', [])
                inserted = len(data) - len(werrors)
                logger.info(f"Saved {inserted} new items to {collection_name} ({len(werrors)} duplicates skipped).")
                return True
        except Exception as e:
            logger.error(f"Error saving to MongoDB ({collection_name}): {e}")
            return False

    async def execute_with_retry(self, func, *args, max_retries=3, base_delay=2, **kwargs):
        """Execute a function with exponential backoff retry logic."""
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Skip backoff on last try
                if attempt == max_retries - 1:
                    logger.error(f"Final attempt failed in {func.__name__}: {e}")
                    raise
                
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Error in {func.__name__}: {e}. Retrying in {delay}s... (Attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(delay)
