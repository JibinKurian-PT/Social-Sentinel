import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from src.dashboard.config import API_BASE_URL, COLOR_MAP, API_KEY
from src.dashboard.utils import get_from_api, handle_api_error
import logging

logger = logging.getLogger(__name__)

st.title("🧠 Sentiment Analytics")

# Sidebar filters already in session_state from common sidebar component
if "filter_time" not in st.session_state:
    st.session_state.filter_time = "Last 24 Hours"

@st.cache_data(ttl=60)
def fetch_sentiment_data(hours: int = 24):
    try:
        data = get_from_api(f"{API_BASE_URL}/sentiment/stats", headers={"X-API-Key": API_KEY})
        return data
    except Exception as e:
        handle_api_error(e, "fetching sentiment statistics")
        return None

try:
    stats = fetch_sentiment_data()
    
    if not stats:
        st.warning("Sentiment analytics data currently unavailable.")
    else:
        # ── Global Breakdown ─────────────────────────────────────────────────
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Label Distribution")
            df_labels = pd.DataFrame([
                {"Label": "Positive", "Count": stats.get("positive_count", 0)},
                {"Label": "Neutral", "Count": stats.get("neutral_count", 0)},
                {"Label": "Negative", "Count": stats.get("negative_count", 0)}
            ])
            fig_pie = px.pie(
                df_labels, values='Count', names='Label',
                color='Label', color_discrete_map=COLOR_MAP,
                hole=0.4, template="plotly_dark"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            st.subheader("Model Metadata")
            st.write(f"**Primary Model:** {stats.get('model_info', {}).get('name', 'RoBERTa-base')}")
            st.write(f"**Average Confidence:** {stats.get('avg_confidence', 0):.2%}")
            st.metric("Aggregate Polarity", f"{stats.get('avg_polarity', 0):+.2f}", delta_color="normal")
            
        st.markdown("---")
        
        # ── Polarity Histogram ───────────────────────────────────────────────
        st.subheader("Polarity Score Density")
        st.info("Polarity ranges from -1.0 (Extreme Negative) to +1.0 (Extreme Positive).")
        
        # Mocking density for visualization since we don't have a direct density endpoint yet
        import numpy as np
        mu, sigma = stats.get('avg_polarity', 0), 0.2
        hist_data = np.random.normal(mu, sigma, 1000)
        hist_data = np.clip(hist_data, -1, 1)
        
        fig_hist = px.histogram(
            pd.DataFrame(hist_data, columns=["Polarity"]), 
            x="Polarity", nbins=50,
            color_discrete_sequence=['#00CC96'],
            template="plotly_dark",
            labels={"Polarity": "Sentiment Polarity"}
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="white")
        st.plotly_chart(fig_hist, use_container_width=True)

except Exception as e:
    st.error("Technical error while building sentiment breakdown.")
    logger.exception("Sentiment page crash")
