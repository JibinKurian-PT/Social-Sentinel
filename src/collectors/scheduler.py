from typing import List
from .twitter_collector import TwitterCollector
from .youtube_collector import YouTubeCollector
import logging

logger = logging.getLogger(__name__)

class CollectionScheduler:
    """Orchestrates collection from multiple platforms."""
    
    def __init__(self):
        self.twitter = TwitterCollector()
        self.youtube = YouTubeCollector()
        
    async def run_all(self, keywords: List[str], max_per_platform: int = 100):
        """Run all collectors for a list of keywords concurrently."""
        logger.info(f"Starting combined collection for {len(keywords)} keywords.")
        
        all_results = {"twitter": [], "youtube": []}
        
        for kw in keywords:
            logger.info(f"Collecting for keyword: {kw}")
            
            # Since collectors wrap blocking calls in asyncio executors, we can await them
            # or we could use asyncio.gather for parallel keyword fetching (omitted here to respect rate limits)
            tw_data = await self.twitter.collect(query=kw, max_results=max_per_platform)
            all_results["twitter"].extend(tw_data)
            
            yt_data = await self.youtube.collect(query=kw, max_results=max_per_platform)
            all_results["youtube"].extend(yt_data)
            
        return all_results
