from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, UniqueConstraint # type: ignore
from sqlalchemy.sql import func # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from .connection import Base

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(String, unique=True, index=True)
    text = Column(Text, nullable=False)
    platform = Column(String, default="twitter", index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    location = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True) # e.g. likes, retweets
    
    sentiment = relationship("SentimentResult", uselist=False, back_populates="tweet", cascade="all, delete-orphan")
    topics = relationship("TopicAssociation", back_populates="tweet", cascade="all, delete-orphan")

class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id", ondelete="CASCADE"), unique=True)
    label = Column(String, index=True) # positive, negative, neutral
    polarity = Column(Float) # -1.0 to 1.0
    confidence = Column(Float)
    model_used = Column(String) # ensemble, bert, textblob
    created_at = Column(DateTime(timezone=True), default=func.now())

    tweet = relationship("Tweet", back_populates="sentiment")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    keywords = Column(JSON) # List of keywords
    volume = Column(Integer, default=0)
    avg_sentiment = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    tweet_associations = relationship("TopicAssociation", back_populates="topic")

class TopicAssociation(Base):
    __tablename__ = "topic_associations"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id", ondelete="CASCADE"))
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"))
    confidence = Column(Float)
    
    tweet = relationship("Tweet", back_populates="topics")
    topic = relationship("Topic", back_populates="tweet_associations")

class DailyAggregate(Base):
    __tablename__ = "daily_aggregates"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), index=True)
    platform = Column(String, index=True)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    avg_polarity = Column(Float, default=0.0)
    
    # Adding unique constraint for date + platform
    __table_args__ = (
        UniqueConstraint('date', 'platform', name='uix_date_platform'),
    )
