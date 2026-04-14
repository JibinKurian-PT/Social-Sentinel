import streamlit as st # type: ignore
from src.dashboard.config import setup_page
from src.dashboard.components.filters import render_sidebar_filters
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure main layout and theme
try:
    setup_page("Social Sentinel Dashboard", "📊")
except Exception as e:
    st.error("Failed to initialize dashboard configuration.")
    logger.error(f"Init error: {e}")

# Render Sidebar
st.sidebar.title("📊 Social Sentinel")
st.sidebar.markdown("Advanced Social Media Intelligence")

try:
    render_sidebar_filters()
except Exception as e:
    st.sidebar.warning("Could not load filters. Check API connectivity.")
    logger.error(f"Sidebar error: {e}")

st.sidebar.markdown("---")
st.sidebar.info("Select a page above to start analyzing data.")

# Main Landing
st.title("Welcome to Social Sentinel")

st.markdown("""
<div style='background-color: #1a1a1a; padding: 2rem; border-radius: 10px; border-left: 4px solid #00CC96; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
    <h3 style='color: #00CC96;'>Real-time Sentiment & Trend Intelligence</h3>
    <p style='color: #e0e0e0;'>Monitor your brand's digital footprint across platforms with state-of-the-art NLP models (RoBERTa + LDA).</p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("### Quick Navigation")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("📈 **Overview**: High-level KPIs and aggregate trends over time.")
    st.info("🧠 **Sentiment**: Deep dive into polarities and confidence margins.")
with col2:
    st.info("🔍 **Topics**: Discover what users are talking about right now via LDA.")
    st.info("⚡ **Realtime**: Watch the live streaming websocket feed.")
with col3:
    st.success("📥 **CSV Analyzer**: Upload your own CSV files for batch sentiment processing.")
    st.success("📊 **CSV Insights**: Auto-generated dashboard from your uploaded data.")

# Initialize session state for CSV processing
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None

# Global Error Boundary fallback
if "error" in st.session_state:
    st.error(f"A global error occurred: {st.session_state['error']}")
    if st.button("Clear Error"):
        del st.session_state["error"]
        st.rerun()
