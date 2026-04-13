"""
Async Data Seeder for Social Sentiment System.
Uses SQLAlchemy async sessions correctly to avoid connection issues.
Populates mock data for testing and initial production visualization.
"""
import asyncio
import random
from datetime import datetime, timedelta
import logging

from sqlalchemy.future import select
from src.database.postgres.connection import async_session_factory, engine
from src.database.postgres.models import Tweet, SentimentResult, Topic, TopicAssociation, DailyAggregate

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MOCK_TOPICS = [
    {"name": "AI & Future tech", "keywords": ["ai", "ml", "chatgpt", "gpu"]},
    {"name": "Climate Change", "keywords": ["climate", "green", "carbon", "environment"]},
    {"name": "Global Economy", "keywords": ["inflation", "rates", "stocks", "market"]},
    {"name": "Cyber Security", "keywords": ["hack", "breach", "password", "security"]},
    {"name": "Consumer Tech", "keywords": ["iphone", "android", "laptop", "review"]}
]

async def seed():
    if not async_session_factory:
        logger.error("DB Session factory not initialized.")
        return

    async with async_session_factory() as session:
        # 1. Seed Topics
        logger.info("Seeding Topics...")
        for t_data in MOCK_TOPICS:
            stmt = select(Topic).where(Topic.name == t_data["name"])
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                topic = Topic(name=t_data["name"], keywords=t_data["keywords"], volume=0)
                session.add(topic)
        await session.commit()

        # Get topic IDs
        res = await session.execute(select(Topic))
        topics = res.scalars().all()
        topic_ids = [t.id for t in topics]

        # 2. Seed Tweets and Sentiment (last 7 days)
        logger.info("Seeding Tweets and Sentiment...")
        tweets_to_add = []
        for i in range(100):
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            platform = random.choice(["twitter", "youtube"])
            
            tweet = Tweet(
                platform=platform,
                platform_id=f"seed_{platform}_{i}_{int(created_at.timestamp())}",
                text=f"Sample post about {random.choice(['the world', 'technology', 'life', 'money'])} {i}",
                created_at=created_at,
                location=random.choice(["New York", "London", "Tokyo", "Berlin", "San Francisco", None]),
                user_id=f"user_{random.randint(1, 1000)}",
                metrics={"likes": random.randint(0, 500)}
            )
            session.add(tweet)
            await session.flush() # gets ID

            # Add Sentiment
            label = random.choice(["positive", "negative", "neutral"])
            pol = random.uniform(-0.8, 0.8)
            res = SentimentResult(
                tweet_id=tweet.id,
                label=label,
                polarity=pol,
                confidence=random.uniform(0.6, 0.99),
                model_used="ensemble_v2"
            )
            session.add(res)

            # Link to topic
            assoc = TopicAssociation(
                tweet_id=tweet.id,
                topic_id=random.choice(topic_ids),
                confidence=random.uniform(0.5, 0.9)
            )
            session.add(assoc)

        await session.commit()

        # 3. Seed Daily Aggregates
        logger.info("Updating Daily Aggregates...")
        for day_offset in range(14):
            day = (datetime.utcnow() - timedelta(days=day_offset)).date()
            for platform in ["twitter", "youtube"]:
                # Check if exists
                stmt = select(DailyAggregate).where(DailyAggregate.date == day, DailyAggregate.platform == platform)
                res = await session.execute(stmt)
                agg = res.scalar_one_or_none()
                
                if not agg:
                    agg = DailyAggregate(
                        date=day,
                        platform=platform,
                        positive_count=random.randint(10, 50),
                        negative_count=random.randint(5, 30),
                        neutral_count=random.randint(20, 100),
                        avg_polarity=random.uniform(-0.2, 0.4)
                    )
                    session.add(agg)
        
        await session.commit()
        logger.info("✅ Seeding complete!")

async def main():
    try:
        await seed()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
