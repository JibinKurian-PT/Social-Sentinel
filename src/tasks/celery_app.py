from celery import Celery # type: ignore
from celery.schedules import crontab # type: ignore
from src.config import settings

# Initialize Celery app
celery_app = Celery(
    "sentiment_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.tasks.collection_tasks", "src.tasks.nlp_tasks"]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max
    worker_prefetch_multiplier=1, # Fair distribution of tasks
)

# Beat Schedule
celery_app.conf.beat_schedule = {
    # Run data collection every 15 minutes
    "collect-twitter-data-15min": {
        "task": "src.tasks.collection_tasks.scheduled_twitter_collection",
        "schedule": crontab(minute="*/15"),
    },
    # Run YouTube heavily rate-limited, every hour
    "collect-youtube-data-hourly": {
        "task": "src.tasks.collection_tasks.scheduled_youtube_collection",
        "schedule": crontab(minute="0"),
    },
    # Process raw data through NLP continuously (every 5 mins)
    "process-raw-data": {
        "task": "src.tasks.nlp_tasks.process_unscored_data",
        "schedule": crontab(minute="*/5"),
    },
    # Retrain LDA model daily at 2 AM
    "retrain-lda-daily": {
        "task": "src.tasks.nlp_tasks.retrain_lda_model",
        "schedule": crontab(hour="2", minute="0"),
    },
    # Aggregate data nightly
    "aggregate-daily-stats": {
        "task": "src.tasks.nlp_tasks.aggregate_daily_stats",
        "schedule": crontab(hour="1", minute="0"),
    }
}
