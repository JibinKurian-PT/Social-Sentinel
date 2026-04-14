import pandas as pd
import requests
import time
import os
import argparse
import logging
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "test_api_key_123456")

def import_kaggle_data(file_path: str, text_col: str, delay: float = 1.0, limit: int = 100):
    """
    Imports data from a Kaggle CSV and simulates a real-time stream.
    
    Args:
        file_path: Path to the CSV file.
        text_col: Name of the column containing the text.
        delay: Seconds to wait between posts (simulation).
        limit: Max rows to process.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    logger.info(f"Loading dataset from {file_path}...")
    df = pd.read_sql
    # Since I don't want to load a giant CSV into memory if it's millions of rows:
    # Use chunksize or head
    df = pd.read_csv(file_path).head(limit)
    
    headers = {"X-API-Key": API_KEY}
    
    logger.info(f"Starting real-time playback of {len(df)} rows with {delay}s delay...")
    
    for _, row in df.iterrows():
        text = str(row[text_col])
        if not text.strip():
            continue
            
        try:
            # 1. Analyze Sentiment
            payload = {"text": text}
            resp = requests.post(f"{API_URL}/sentiment/analyze", json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            
            # 2. Prepare Broadcast Payload for Dashboard
            broadcast_msg = {
                "platform": "kaggle_import",
                "user": "Dataset User",
                "text": text,
                "sentiment": {
                    "label": result["label"],
                    "confidence": result["confidence"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # 3. Trigger Real-time Dashboard Update
            requests.post(f"{API_URL}/broadcast", json=broadcast_msg, headers=headers)
            
            logger.info(f"Processed: {text[:50]}... [{result['label'].upper()}]")
            
            # 4. Simulation Delay
            time.sleep(delay)
            
        except Exception as e:
            logger.error(f"Error processing row: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate real-time Kaggle data ingestion.")
    parser.add_argument("--file", type=str, required=True, help="Path to Kaggle CSV")
    parser.add_argument("--col", type=str, default="text", help="Name of text column")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between rows")
    parser.add_argument("--limit", type=int, default=50, help="Max rows to import")
    
    args = parser.parse_args()
    
    import_kaggle_data(args.file, args.col, args.delay, args.limit)
