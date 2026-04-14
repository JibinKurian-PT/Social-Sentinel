FROM python:3.11-slim as base

WORKDIR /app

ENV PYTHONPATH=/app
ENV HF_HOME=/app/.cache/huggingface
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK and SpaCy
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt_tab');"
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Pre-download BERT model (The heaviest step)
COPY src/config.py src/
RUN python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; model_name='cardiffnlp/twitter-roberta-base-sentiment-latest'; AutoTokenizer.from_pretrained(model_name); AutoModelForSequenceClassification.from_pretrained(model_name);"

# Copy application code and assets
COPY src/ src/
COPY static/ static/
COPY alembic.ini .
COPY scripts/ scripts/
COPY tests/ tests/

# Default CMD (can be overridden in docker-compose)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
