import asyncio
from googleapiclient.discovery import build # type: ignore
from googleapiclient.errors import HttpError # type: ignore
from typing import List, Dict, Any
from datetime import datetime
import logging
from .base_collector import BaseCollector
from src.config import settings

logger = logging.getLogger(__name__)

class YouTubeCollector(BaseCollector):
    def __init__(self):
        try:
            if not settings.YOUTUBE_API_KEY:
                logger.warning("YouTube API Key not found in config. Collector will run in mock mode.")
                self.youtube = None
            else:
                self.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        except Exception as e:
            logger.error(f"Error initializing YouTube client: {e}")
            self.youtube = None

    async def collect(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Fetch video comments matching a query."""
        if not self.youtube:
            return self._generate_mock_data(query, max_results)
            
        results = []
        try:
            loop = asyncio.get_event_loop()
            
            def search_videos():
                return self.youtube.search().list(
                    q=query,
                    part='id,snippet',
                    maxResults=min(max_results // 10 + 1, 25), # Assume avg 10 comments per video
                    type='video',
                    order='date'
                ).execute()

            search_response = await loop.run_in_executor(None, search_videos)
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            for video_id in video_ids:
                if len(results) >= max_results:
                    break
                    
                def fetch_comments():
                    return self.youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=min(max_results - len(results), 100),
                        textFormat='plainText'
                    ).execute()
                    
                try:
                    comments_response = await loop.run_in_executor(None, fetch_comments)
                    
                    for item in comments_response.get('items', []):
                        top_comment = item['snippet']['topLevelComment']['snippet']
                        results.append({
                            "platform_id": f"yt_{item['id']}",
                            "video_id": video_id,
                            "text": top_comment['textDisplay'],
                            "created_at": datetime.strptime(top_comment['publishedAt'], "%Y-%m-%dT%H:%M:%SZ"),
                            "author_id": top_comment.get('authorChannelId', {}).get('value', 'unknown'),
                            "author_username": top_comment.get('authorDisplayName', 'unknown'),
                            "metrics": {
                                "like_count": top_comment.get('likeCount', 0)
                            },
                            "platform": "youtube",
                            "query": query,
                            "collected_at": datetime.utcnow()
                        })
                        
                        if len(results) >= max_results:
                            break
                            
                except HttpError as e:
                    if 'disabled comments' in str(e).lower() or e.resp.status == 403:
                        logger.info(f"Comments disabled for video {video_id}")
                        continue
                    else:
                        raise e
                        
        except Exception as e:
            logger.error(f"Error during YouTube collection for query '{query}': {e}")
            
        return results
        
    def _generate_mock_data(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Fallback mock data generation if no API keys."""
        import random
        return [
            {
                "platform_id": f"mock_yt_{random.randint(10000, 99999)}",
                "text": f"This video explains {query} perfectly!",
                "created_at": datetime.utcnow(),
                "author_id": "mock_yt_author",
                "author_username": "yt_watcher",
                "metrics": {"like_count": random.randint(0, 500)},
                "platform": "youtube",
                "query": query,
                "collected_at": datetime.utcnow()
            } for _ in range(count)
        ]
