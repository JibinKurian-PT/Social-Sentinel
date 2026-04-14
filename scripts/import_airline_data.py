import asyncio
import aiohttp
import pandas as pd
import json
import argparse
import os
from datetime import datetime
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AirlineDataImporter:
    def __init__(self, api_url="http://localhost:8000", api_key="test_api_key_123456"):
        self.api_url = api_url
        self.api_key = api_key
        self.processed_count = 0
        
    async def send_to_api(self, session, text, row_data):
        """Send a single tweet to the sentiment API and broadcast it to the dashboard."""
        # 1. Analyze via API
        payload = {
            "text": text
        }
        headers = {"X-API-Key": self.api_key}
        
        try:
            async with session.post(
                f"{self.api_url}/api/v1/sentiment/analyze",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # 2. Prepare Broadcast Payload for Real-time Dashboard
                    broadcast_msg = {
                        "platform": f"Airline: {row_data.get('airline', 'unknown')}",
                        "user": row_data.get('name', 'anonymous'),
                        "text": text,
                        "sentiment": {
                            "label": result["label"],
                            "confidence": result["confidence"]
                        },
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {
                            "original_sentiment": row_data.get('airline_sentiment', 'unknown'),
                            "airline": row_data.get('airline', 'unknown')
                        }
                    }
                    
                    # 3. Trigger Dashboard Update
                    await session.post(
                        f"{self.api_url}/api/v1/broadcast",
                        json=broadcast_msg,
                        headers=headers
                    )
                    
                    self.processed_count += 1
                    return result
                else:
                    logger.error(f"API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    async def stream_dataset(self, file_path, text_col="text", delay=0.5, limit=None):
        """Stream dataset through API"""
        logger.info(f"Loading dataset from {file_path}")
        
        try:
            # Load CSV in chunks if needed, but here we just read it
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return
        
        if limit:
            df = df.head(limit)
        
        logger.info(f"Streaming {len(df)} tweets with {delay}s delay")
        
        async with aiohttp.ClientSession() as session:
            for idx, row in tqdm(df.iterrows(), total=len(df), desc="Streaming tweets"):
                text = row[text_col]
                
                if pd.isna(text) or len(str(text)) < 5:
                    continue
                
                await self.send_to_api(session, str(text), row.to_dict())
                
                if delay > 0:
                    await asyncio.sleep(delay)
        
        logger.info(f"✅ Complete! Processed {self.processed_count} tweets")

async def main():
    parser = argparse.ArgumentParser(description="Stream airline sentiment dataset")
    parser.add_argument("--file", type=str, default="data/raw/Tweets.csv", help="Path to CSV file")
    parser.add_argument("--col", type=str, default="text", help="Column name containing text")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between tweets")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tweets")
    parser.add_argument("--api", type=str, default="http://localhost:8000", help="API base URL")
    parser.add_argument("--key", type=str, default="test_api_key_123456", help="API Key")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return
    
    importer = AirlineDataImporter(api_url=args.api, api_key=args.key)
    await importer.stream_dataset(
        file_path=args.file,
        text_col=args.col,
        delay=args.delay,
        limit=args.limit
    )

if __name__ == "__main__":
    asyncio.run(main())
