import logging
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from src.config import settings

logger = logging.getLogger(__name__)

class MongoDBConnection:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDBConnection()

async def connect_to_mongo():
    if db_instance.client is None:
        try:
            db_instance.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            db_instance.db = db_instance.client[settings.MONGO_DB]
            
            # Ensure indexes are created for performance
            await _create_indexes()
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")

async def _create_indexes():
    """Create indexes on the raw data collections to optimize querying."""
    if db_instance.db is not None:
        try:
            raw_tweets = db_instance.db["raw_twitter"]
            await raw_tweets.create_index("created_at")
            await raw_tweets.create_index("platform_id", unique=True)
            await raw_tweets.create_index([("author_id", 1)])
            
            raw_youtube = db_instance.db["raw_youtube"]
            await raw_youtube.create_index("created_at")
            await raw_youtube.create_index("platform_id", unique=True)
            await raw_youtube.create_index([("video_id", 1)])
        except Exception as e:
            logger.warning(f"Could not create MongoDB indexes: {e}")

async def get_mongo_db():
    if db_instance.client is None:
        await connect_to_mongo()
    return db_instance.db

def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")
