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
        topic_names = []
        for t in topics:
            t_id = t.get("topic_id", t.get("id", "Unknown"))
            keywords = t.get("keywords", [])
            name = t.get("name", f"Topic {t_id}")
            label = f"{name}: {', '.join(keywords[:3])}..."
            topic_names.append(label)

        selected_idx = st.sidebar.selectbox("Select Topic Details", range(len(topics)), format_func=lambda x: topic_names[x])
        
        selected_topic = topics[selected_idx]
        t_id = selected_topic.get("topic_id", selected_topic.get("id", "N/A"))
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Keywords for Cluster {t_id}")
            
            keywords = selected_topic.get("keywords", [])
            weights = selected_topic.get("weights", [0.5] * len(keywords))
            
            if not keywords:
                st.info("No keywords found for this cluster.")
            else:
                df_words = pd.DataFrame({
                    "Keyword": keywords,
                    "Weight": weights
                }).sort_values("Weight", ascending=True)
                
                fig_topic = px.bar(
                    df_words, x="Weight", y="Keyword", orientation='h',
                    color="Weight", color_continuous_scale="Viridis",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_topic, use_container_width=True)
            
        with col2:
            st.subheader("Cluster Info")
            volume = selected_topic.get("volume", 0)
            avg_sent = selected_topic.get("avg_sentiment", 0.0)
            
            st.metric("Engagement Volume", f"{volume}")
            st.metric("Avg Sentiment", f"{avg_sent:.2f}")
            st.markdown("""
            **Summary:** This cluster represents discussions centered around 
            these primary keywords. Higher weights indicate stronger semantic 
            relevance to the topic model.
            """)

except Exception as e:
    st.error("Failed to render Topic Analysis dashboard.")
    logger.exception("Topics page crash")

import random # for mock data inside try block
