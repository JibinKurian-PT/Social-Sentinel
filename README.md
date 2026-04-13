# Production Social Media Sentiment & Trend Analysis System

A comprehensive, production-ready system to collect, analyze, and visualize sentiment and trends from social media platforms.
Built with FastAPI, Streamlit, Celery, HuggingFace Transformers (BERT), PostgreSQL, MongoDB, and Redis.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌───────────────┐
│   Twitter   │     │   YouTube   │     │  Other APIs   │
└──────┬──────┘     └──────┬──────┘     └───────┬───────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌───────────────────────────────────────────────────────┐
│               Celery Workers (Collectors)             │
│   Rate Limiting, Retries, Exponential Backoff         │
└──────┬────────────────────────────────────────┬───────┘
       │                                        │
       ▼                                        │
┌─────────────┐                         ┌───────▼───────┐
│   MongoDB   │◄────────────────────────┤  Celery Tasks │
│ (Raw Data)  │                         │ (NLP Engine)  │
└─────────────┘                         └───────┬───────┘
                                                │
                                                ▼
┌─────────────┐     ┌───────────────────────────────────┐
│    Redis    │◄────┤            FastAPI Backend        │
│  (Caching)  │     │   REST Endpoints & WebSockets     │
└─────────────┘     └─────────────────┬─────────────────┘
                                      │
                                      ▼
┌─────────────┐               ┌───────────────┐
│ PostgreSQL  │◄──────────────┤   Streamlit   │
│ (Aggregates)│               │   Dashboard   │
└─────────────┘               └───────────────┘
```

## Setup & Running

1. Clone and configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and supply your valid API keys for full data
   ```

2. Using Docker Compose (Recommended)
   ```bash
   make docker-up
   ```

3. Local Development (Python 3.11+)
   Ensure PostgreSQL, MongoDB, and Redis are running locally.
   ```bash
   python -m venv venv
   source venv/bin/activate
   make install
   make install-dev
   
   # Setup Database Schema
   make migrate
   
   # Run the 3 main components in separate terminals
   make run-api
   make run-worker
   make run-dashboard
   ```

## Development & Testing
```bash
make test    # Run pytest
make lint    # Run flake8 and mypy
make format  # Run black and isort
make seed    # Generate test data without requiring real API keys
```

## Dashboard Features
- **Overview**: KPIs, general sentiment volume over time.
- **Sentiment**: Deep dive into score distributions, confidence margins.
- **Topics**: LDA topic modeling visualizations, word clouds.
- **GeoMap**: Mapping origin of posts and regional sentiment.
- **Realtime**: WebSocket feed simulating/tracking live data.
