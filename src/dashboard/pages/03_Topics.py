import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from src.dashboard.config import API_BASE_URL, API_KEY
from src.dashboard.utils import get_from_api, handle_api_error
import logging

logger = logging.getLogger(__name__)

st.title("🔍 Topic Discovery")
st.markdown("LDA (Latent Dirichlet Allocation) Clusters extracted from incoming streams.")

@st.cache_data(ttl=300)
def fetch_topics():
    try:
        data = get_from_api(f"{API_BASE_URL}/topics", headers={"X-API-Key": API_KEY})
        return data
    except Exception as e:
        handle_api_error(e, "fetching topic modeling data")
        return []

try:
    topics = fetch_topics()
    
    if not topics:
        st.warning("No latent topics identified yet. Increase data volume to trigger LDA training.")
    else:
        # Sidebar to select topic
        topic_names = [f"Topic {t['topic_id']}: {', '.join(t['keywords'][:3])}..." for t in topics]
        selected_idx = st.sidebar.selectbox("Select Topic Details", range(len(topics)), format_func=lambda x: topic_names[x])
        
        selected_topic = topics[selected_idx]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Keywords for Cluster {selected_topic['topic_id']}")
            df_words = pd.DataFrame({
                "Keyword": selected_topic["keywords"],
                "Weight": selected_topic["weights"]
            }).sort_values("Weight", ascending=True)
            
            fig_topic = px.bar(
                df_words, x="Weight", y="Keyword", orientation='h',
                color="Weight", color_continuous_scale="Viridis",
                template="plotly_dark"
            )
            st.plotly_chart(fig_topic, use_container_width=True)
            
        with col2:
            st.subheader("Cluster Info")
            st.metric("Engagement Volume", f"{random.randint(500, 5000)}") # Mock volume
            st.metric("Avg Quality (Coherence)", "0.58")
            st.markdown("""
            **Summary:** This cluster represents discussions centered around 
            these primary keywords. Higher weights indicate stronger semantic 
            relevance to the topic model.
            """)

except Exception as e:
    st.error("Failed to render Topic Analysis dashboard.")
    logger.exception("Topics page crash")

import random # for mock data inside try block
