import streamlit as st
import pandas as pd
import time
import random

class RealTimeCSVFeed:
    """
    Simulates a real-time streaming feed from a pre-processed CSV file.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        if "sentiment_label" not in df.columns:
            st.warning("Feed requires analyzed sentiment labels.")

    def render(self):
        st.markdown("### ⚡ Live Stream Simulation")
        
        # Controls
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            start = st.button("▶️ Play Feed")
        with col2:
            stop = st.button("⏹️ Stop")
        with col3:
            speed = st.select_slider("Stream Speed", options=["Slow", "Normal", "Fast"], value="Normal")
            
        delay = {"Slow": 2.0, "Normal": 0.8, "Fast": 0.2}[speed]
        
        # Container for the live feed
        feed_container = st.empty()
        gauge_container = st.empty()
        
        if start:
            st.session_state.streaming = True
            
            # Simple simulation loop
            for idx, row in self.df.iterrows():
                if not st.session_state.get("streaming", True):
                    break
                    
                # Update Gauge
                polarity = row.get("sentiment_polarity", 0)
                sentiment = row.get("sentiment_label", "neutral")
                
                # Render Feed Item with Card styling
                color = "#00CC96" if sentiment == "positive" else "#EF553B" if sentiment == "negative" else "#AB63FA"
                
                with feed_container.container():
                    st.markdown(f"""
                    <div style='background-color: #262730; padding: 1rem; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 1rem;'>
                        <p style='color: #888; font-size: 0.8rem; margin-bottom: 0.2rem;'>Post #{idx} | {row.get('location', 'Global')}</p>
                        <p style='color: white; font-size: 1rem;'>{row.get('text', '')}</p>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='color: {color}; font-weight: bold;'>{sentiment.upper()}</span>
                            <span style='color: #555; font-size: 0.8rem;'>Confidence: {row.get('sentiment_confidence', 0):.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(delay)
                
        if stop:
            st.session_state.streaming = False
            st.info("Stream stopped.")
