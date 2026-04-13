import tweepy # type: ignore
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .base_collector import BaseCollector
from src.config import settings

logger = logging.getLogger(__name__)

class TwitterCollector(BaseCollector):
    def __init__(self):
        try:
            if not settings.TWITTER_BEARER_TOKEN:
                logger.warning("Twitter Bearer Token not found in config. Collector will run in mock mode.")
                self.client = None
            else:
                self.client = tweepy.Client(
                    bearer_token=settings.TWITTER_BEARER_TOKEN,
                    wait_on_rate_limit=True,
                    return_type=dict
                )
        except Exception as e:
            logger.error(f"Error initializing Twitter client: {e}")
            self.client = None

    async def collect(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent tweets for a query."""
        if not self.client:
            logger.info("Running in mock mode for Twitter")
            return self._generate_mock_data(query, max_results)
            
        results = []
        try:
            # We must use execute_with_retry to wrap the blocking tweepy call within asyncio
            loop = asyncio.get_event_loop()
            
            def fetch_tweets():
                return self.client.search_recent_tweets(
                    query=f"{query} -is:retweet lang:en",
                    max_results=min(max_results, 100), # v2 max per page is 100
                    tweet_fields=['created_at', 'author_id', 'lang', 'public_metrics', 'geo'],
                    user_fields=['username'],
                    expansions=['author_id', 'geo.place_id']
                )

            # Using ThreadPoolExecutor implicitly via run_in_executor
            response = await loop.run_in_executor(None, fetch_tweets)
            
            if 'data' in response:
                users = {u['id']: u for u in response.get('includes', {}).get('users', [])}
                places = {p['id']: p for p in response.get('includes', {}).get('places', [])}
                
                for tweet in response['data']:
                    author = users.get(tweet.get('author_id', ''))
                    
                    geo_info = None
                    if 'geo' in tweet and 'place_id' in tweet['geo']:
                        place = places.get(tweet['geo']['place_id'])
                        if place:
                            geo_info = place.get('full_name')
                    
                    results.append({
                        "platform_id": f"tw_{tweet['id']}",
                        "text": tweet['text'],
                        "created_at": datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00')),
                        "author_id": str(tweet.get('author_id')),
                        "author_username": author['username'] if author else "unknown",
                        "metrics": tweet.get('public_metrics', {}),
                        "language": tweet.get('lang'),
                        "location": geo_info,
                        "platform": "twitter",
                        "query": query,
                        "collected_at": datetime.utcnow()
                    })
        except tweepy.errors.TooManyRequests as e:
            logger.error("Twitter Rate Limit Reached.")
            raise e
        except Exception as e:
            logger.error(f"Error during Twitter collection for query '{query}': {e}")
            
        return results
        
    def _generate_mock_data(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Fallback mock data generation if no API keys."""
        import random
        return [
            {
                "platform_id": f"mock_tw_{random.randint(10000, 99999)}",
                "text": f"Just exploring the new features of {query}! #tech",
                "created_at": datetime.utcnow(),
                "author_id": "mock_author",
                "author_username": "mockingbird",
                "metrics": {"like_count": random.randint(0, 100)},
                "platform": "twitter",
                "query": query,
                "collected_at": datetime.utcnow()
            } for _ in range(count)
        ]
