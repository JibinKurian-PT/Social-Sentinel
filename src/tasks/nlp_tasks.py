import asyncio
from celery import shared_task # type: ignore
import logging
from typing import List, Dict, Any

from src.database.mongo.connection import get_mongo_db
from src.database.postgres.connection import async_session_factory
from src.database.postgres.models import Tweet, SentimentResult, Topic, TopicAssociation, DailyAggregate
from src.nlp.sentiment.ensemble_analyzer import EnsembleAnalyzer
from src.nlp.topic_modeling.lda_model import LDA_TopicModel
from src.nlp.topic_modeling.topic_labeler import TopicLabeler
from sqlalchemy.future import select # type: ignore
from sqlalchemy import func, funcfilter # type: ignore
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@shared_task(bind=True, time_limit=3600)
def process_unscored_data(self):
    """Scan Mongo for raw data not yet in Postgres, process NLP, save to Postgres."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_async_process_unscored())

async def _async_process_unscored():
    db = await get_mongo_db()
    if not async_session_factory:
        logger.error("No async session factory available for NLP processing.")
        return
        
    async with async_session_factory() as session:
        # Check what we already processed by getting max created_at
        stmt = select(func.max(Tweet.created_at))
        result = await session.execute(stmt)
        last_processed = result.scalar()
        
        mongo_query = {}
        if last_processed:
            mongo_query = {"created_at": {"$gt": last_processed}}
            
        analyzer = EnsembleAnalyzer()
        lda = LDA_TopicModel()
        lda_loaded = lda.load_model()
            
        total_processed = 0
        platforms = ["raw_twitter", "raw_youtube"]
        
        for platform_coll in platforms:
            cursor = db[platform_coll].find(mongo_query).sort("created_at", 1).limit(500)
            
            # Gather batch
            documents = []
            async for doc in cursor:
                documents.append(doc)
                
            if not documents:
                continue
                
            total_processed += len(documents)
            texts = [doc["text"] for doc in documents]
            
            # Analyze Sentiment
            sentiment_results = analyzer.analyze_batch(texts)
            
            # Save to PG
            for idx, doc in enumerate(documents):
                s_res = sentiment_results[idx]
                
                # Check exist
                t_check = await session.execute(select(Tweet).where(Tweet.platform_id == doc["platform_id"]))
                if t_check.scalar_one_or_none():
                    continue # skip duplicates
                    
                new_tweet = Tweet(
                    platform_id=doc["platform_id"],
                    text=doc["text"],
                    platform=doc["platform"],
                    created_at=doc["created_at"],
                    location=doc.get("location"),
                    user_id=doc.get("author_id"),
                    metrics=doc.get("metrics", {})
                )
                session.add(new_tweet)
                await session.flush() # get ID
                
                new_sentiment = SentimentResult(
                    tweet_id=new_tweet.id,
                    label=s_res["label"],
                    polarity=s_res["polarity"],
                    confidence=s_res["confidence"],
                    model_used=s_res["model_used"]
                )
                session.add(new_sentiment)
                
                # Assign topic if we have a model
                if lda_loaded:
                    t_res = lda.predict_topic(doc["text"])
                    if t_res["topic_id"] != -1 and t_res["confidence"] > 0.3:
                        # Find or create topic row
                        topic_model = await session.execute(select(Topic).where(Topic.id == t_res["topic_id"]))
                        topic = topic_model.scalar_one_or_none()
                        
                        if not topic:
                            # We don't have this topic in PG yet, shouldn't happen if we serialize correctly, 
                            # but handle gracefully
                            topic = Topic(id=t_res["topic_id"], name=f"Topic {t_res['topic_id']}", keywords=[])
                            session.add(topic)
                            await session.flush()
                            
                        assoc = TopicAssociation(
                            tweet_id=new_tweet.id,
                            topic_id=topic.id,
                            confidence=t_res["confidence"]
                        )
                        session.add(assoc)
                        
            await session.commit()
            
    return f"Processed {total_processed} new posts."

@shared_task
def retrain_lda_model():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_async_retrain_lda())

async def _async_retrain_lda():
    if not async_session_factory:
        return "Failed: No DB context."
        
    async with async_session_factory() as session:
        # Get recent texts
        stmt = select(Tweet.text).order_by(Tweet.created_at.desc()).limit(10000)
        result = await session.execute(stmt)
        docs = [row[0] for row in result.all()]
        
        if len(docs) < 100:
            return "Not enough data to train."
            
        lda = LDA_TopicModel()
        train_res = lda.train(docs)
        
        if train_res["status"] == "success":
            lda.save_model()
            
            # Update PG Topics Table
            for t in train_res["topics"]:
                name = TopicLabeler.generate_label(t["keywords"])
                
                existing = await session.execute(select(Topic).where(Topic.id == t["topic_id"]))
                topic_row = existing.scalar_one_or_none()
                
                if topic_row:
                    topic_row.name = name
                    topic_row.keywords = t["keywords"]
                else:
                    topic_row = Topic(
                        id=t["topic_id"],
                        name=name,
                        keywords=t["keywords"]
                    )
                    session.add(topic_row)
                    
            await session.commit()
            return f"LDA trained successfully. Coherence: {train_res['coherence']}"
    return "Failed."

@shared_task
def aggregate_daily_stats():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_async_aggregate())

async def _async_aggregate():
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    # implementation omitted for brevity, would query count and average group by platform and date
    return "Aggregated (mock)"
