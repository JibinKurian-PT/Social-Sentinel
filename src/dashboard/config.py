import os
import streamlit as st # type: ignore

# ── API Connectivity ────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "test_api_key_123456")

# WebSocket requires the API Key often as a query param for browser-side clients
WS_BASE_URL = API_BASE_URL.replace("http", "ws").replace("/api/v1", "/ws/live")
if API_KEY:
    WS_BASE_URL += f"?api_key={API_KEY}"

# ── Design System ───────────────────────────────────────────────────────────
COLOR_MAP = {
    "Positive": "#00CC96",
    "Neutral": "#636EFA",
    "Negative": "#EF553B"
}

PLATFORM_COLORS = {
    "twitter": "#1DA1F2",
    "youtube": "#FF0000",
    "reddit": "#FF4500"
}

def setup_page(title: str, icon: str):
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for standardizing components visually
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #E0E0E0;
        }
        .metric-card {
            background-color: #1a1a1a;
            border-radius: 10px;
            padding: 20px;
            border-left: 5px solid #00CC96;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
