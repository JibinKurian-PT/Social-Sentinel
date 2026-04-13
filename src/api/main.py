from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from prometheus_client import make_asgi_app # type: ignore
import logging

from src.api.routers import sentiment, trends, topics, geo, health
from src.api.websocket.manager import manager
from src.api.websocket.handlers import handle_websocket_messages
from src.api.middleware.auth import APIKeyMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.nlp.topic_modeling.lda_model import lda_model

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting API server.")
    logger.info("Initializing NLP models...")
    try:
        from scripts.migrate_db import run_migrations_programmatically
        await run_migrations_programmatically()
        from src.nlp.sentiment.bert_analyzer import bert_analyzer
        bert_analyzer.load_model()
        await lda_model.train_if_needed()
        logger.info("Startup sequence complete.")
    except Exception as e:
        logger.error(f"Startup error: {e}")
    yield
    # Shutdown
    logger.info("Shutting down API server.")

app = FastAPI(
    title="Social Media Sentiment API",
    description="Production-ready API for Sentiment and Trend Analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Authentication Middleware
app.add_middleware(APIKeyMiddleware)

# Rate Limiting Middleware (100 req per minute)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint at /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include Routers
app.include_router(sentiment.router, prefix="/api/v1")
app.include_router(trends.router, prefix="/api/v1")
app.include_router(topics.router, prefix="/api/v1")
app.include_router(geo.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """Realtime WebSocket Feed."""
    await manager.connect(websocket)
    try:
        await handle_websocket_messages(websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected.")
