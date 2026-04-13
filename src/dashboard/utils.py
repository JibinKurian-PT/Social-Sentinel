"""
Utility functions for the Streamlit dashboard.
Includes retry logic for API calls using Tenacity.
"""
import requests
import streamlit as st # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type # type: ignore
import logging

logger = logging.getLogger(__name__)

def handle_api_error(e: Exception, context: str = "operation"):
    """Standardized error display for dashboard."""
    st.error(f"⚠️ Error during {context}: {str(e)}")
    logger.error(f"Dashboard API Error [{context}]: {e}")

# Retry decorator: 3 attempts, exponential backoff (1s, 2s, 4s)
api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError)),
    reraise=True
)

@api_retry
def get_from_api(url: str, headers: dict = None):
    """Wrapper for requests.get with baked-in retry logic."""
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

@api_retry
def post_to_api(url: str, json_data: dict = None, headers: dict = None):
    """Wrapper for requests.post with baked-in retry logic."""
    response = requests.post(url, json=json_data, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
