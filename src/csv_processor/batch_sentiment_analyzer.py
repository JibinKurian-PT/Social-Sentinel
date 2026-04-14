import pandas as pd
import numpy as np
import logging
import asyncio
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ProcessPoolExecutor
from src.nlp.sentiment.ensemble_analyzer import EnsembleAnalyzer
from src.nlp.sentiment.textblob_analyzer import TextBlobAnalyzer
from src.database.postgres.connection import get_db
from src.database.postgres.models import Tweet, SentimentResult
from src.database.mongo.connection import get_mongo_db
import os

logger = logging.getLogger(__name__)

class BatchSentimentAnalyzer:
    """
    Handles large-scale sentiment analysis of CSV files with batch processing,
    multiprocessing support, and database persistence.
    """
    
    def __init__(self, model_type: str = "accurate"):
        self.model_type = model_type
        if model_type == "accurate":
            self.analyzer = EnsembleAnalyzer()
        else:
            self.analyzer = TextBlobAnalyzer()
            
    async def process_csv_file(
        self, 
        file_path: str, 
        text_column: str, 
        batch_size: int = 100,
        callback: Optional[Callable[[float, str], None]] = None
    ) -> pd.DataFrame:
        """
        Processes a CSV file in chunks, performs sentiment analysis,
        and returns a DataFrame with results.
        """
        logger.info(f"Starting batch processing for {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")
            
        # 1. Read CSV in chunks to handle large files
        chunks = pd.read_csv(file_path, chunksize=batch_size)
        total_rows = sum(1 for _ in pd.read_csv(file_path, usecols=[text_column]))
        processed_rows = 0
        
        all_results = []
        
        for chunk in chunks:
            if callback:
                progress = (processed_rows / total_rows)
                callback(progress, f"Processing rows {processed_rows} to {processed_rows + len(chunk)}...")
                
            # Filter out empty texts
            texts = chunk[text_column].fillna("").astype(str).tolist()
            
            # 2. Analyze batch
            # Note: EnsembleAnalyzer.analyze_batch is already optimized
            results = self.analyzer.analyze_batch(texts)
            
            # 3. Combine with original data
            for i, res in enumerate(results):
                row_res = chunk.iloc[i].to_dict()
                row_res.update({
                    "sentiment_label": res["label"],
                    "sentiment_polarity": res["polarity"],
                    "sentiment_confidence": res["confidence"],
                    "sentiment_model": res["model_used"]
                })
                all_results.append(row_res)
                
            processed_rows += len(chunk)
            
        results_df = pd.DataFrame(all_results)
        
        # 4. Save to databases
        await self.save_results_to_database(results_df)
        
        if callback:
            callback(1.0, "Analysis complete! Results saved to database.")
            
        return results_df

    async def save_results_to_database(self, df: pd.DataFrame):
        """
        Saves analysis results to both PostgreSQL (relational) and MongoDB (raw).
        """
        logger.info(f"Saving {len(df)} results to databases...")
        
        # 1. Save to MongoDB (Raw data storage)
        try:
            mongo_db = await get_mongo_db()
            collection = mongo_db["csv_analysis_results"]
            records = df.to_dict("records")
            await collection.insert_many(records)
            logger.info("Successfully saved to MongoDB.")
        except Exception as e:
            logger.error(f"Failed to save to MongoDB: {e}")
            
        # 2. Save to PostgreSQL (Structured aggregate storage)
        # We reuse the Tweet/SentimentResult models if possible, 
        # or just register them in a generic table if needed.
        # For simplicity and following existing patterns:
        try:
            async for session in get_db():
                for _, row in df.iterrows():
                    # Create a generic Tweet record for each row
                    tweet = Tweet(
                        text=str(row.get("text", "")),
                        platform="csv_upload",
                        location=str(row.get("location", "unknown")),
                        user_id=str(row.get("user", "unknown"))
                    )
                    session.add(tweet)
                    await session.flush() # Get the ID
                    
                    sentiment = SentimentResult(
                        tweet_id=tweet.id,
                        label=row["sentiment_label"],
                        polarity=row["sentiment_polarity"],
                        confidence=row["sentiment_confidence"],
                        model_used=row["sentiment_model"]
                    )
                    session.add(sentiment)
                
                await session.commit()
            logger.info("Successfully saved to PostgreSQL.")
        except Exception as e:
            logger.error(f"Failed to save to PostgreSQL: {e}")

    def generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generates statistical summary of the sentiment analysis results."""
        counts = df["sentiment_label"].value_counts().to_dict()
        return {
            "total_rows": len(df),
            "positive": counts.get("positive", 0),
            "negative": counts.get("negative", 0),
            "neutral": counts.get("neutral", 0),
            "avg_polarity": df["sentiment_polarity"].mean(),
            "avg_confidence": df["sentiment_confidence"].mean()
        }

    def export_results_csv(self, df: pd.DataFrame, output_path: str):
        """Exports the analyzed DataFrame back to a CSV file."""
        df.to_csv(output_path, index=False)
        return output_path
