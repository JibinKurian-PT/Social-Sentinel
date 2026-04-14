import streamlit as st
import pandas as pd
from src.dashboard.config import setup_page
from src.csv_processor.visualization_generator import VisualizationGenerator
from src.dashboard.components.real_time_csv_feed import RealTimeCSVFeed

# Page Configuration
setup_page("CSV Insights Dashboard", "📊")

# Load Custom CSS
with open("static/custom_csv_style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📊 CSV Insights Dashboard")

# Session State Check
if "processed_df" not in st.session_state:
    st.warning("No data found. Please upload and analyze a CSV file on the 'CSV Analyzer' page first.")
    if st.button("Go to CSV Analyzer"):
        # In multi-page apps, this is trickier, but we can instruct the user
        st.info("Select '06 CSV Analyzer' from the sidebar.")
    st.stop()

df = st.session_state.processed_df
viz = VisualizationGenerator()

# Detection
col_info = viz.detect_column_types(df)

# Sidebar Filters
st.sidebar.title("🛠️ Dashboard Controls")
if col_info["categorical"]:
    selected_cat = st.sidebar.selectbox("Breakdown by Segment", ["None"] + col_info["categorical"])
else:
    selected_cat = "None"

# Header Statistics
c1, c2, c3, c4 = st.columns(4)
counts = df["sentiment_label"].value_counts()
c1.metric("Total Records", len(df))
c2.metric("Positive", counts.get("positive", 0), delta=None)
c3.metric("Negative", counts.get("negative", 0), delta_color="inverse")
c4.metric("Avg Polarity", f"{df['sentiment_polarity'].mean():.2f}")

# Main Layout
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visual Analytics", "☁️ Keywords", "📈 Engagement", "📟 Live Simulation"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(viz.create_sentiment_pie(df), use_container_width=True)
        
    with col2:
        st.plotly_chart(viz.create_polarity_histogram(df), use_container_width=True)

    # Trend vs Category section
    c_trend, c_cat = st.columns(2)
    with c_trend:
        if col_info["date"]:
            date_col = st.selectbox("Select Date Column", col_info["date"])
            st.plotly_chart(viz.create_trend_chart(df, date_col), use_container_width=True)
        else:
            st.info("📅 No date column detected for trend analysis.")
            
    with c_cat:
        # Prioritize 'Platform' or 'Country' if available for the default category view
        default_cat = selected_cat
        if default_cat == "None":
            best_cats = [c for c in col_info["categorical"] if c.lower() in ["platform", "country", "source"]]
            if best_cats:
                default_cat = best_cats[0]
        
        if default_cat != "None":
            st.plotly_chart(viz.create_category_bar(df, default_cat), use_container_width=True)
        else:
            st.info("🏷️ Select a category in the sidebar to see breakdowns.")

    # Correlation Heatmap
    if col_info["numeric"]:
        with st.expander("🔢 Feature Correlation"):
            st.plotly_chart(viz.create_correlation_heatmap(df), use_container_width=True)

with tab2:
    st.markdown("### ☁️ Top Keywords & Topic Focus")
    # We find the text column (best guess or the one analyzed)
    text_cols = [c for c in df.columns if "text" in c.lower() or c in col_info["text"]]
    if text_cols:
        wc_b64 = viz.create_wordcloud_base64(df, text_cols[0])
        st.markdown(f'<img src="data:image/png;base64,{wc_b64}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
    else:
        st.warning("Could not identify text column for word cloud.")
        
    st.markdown("### 🔝 Top Examples")
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.success("Positive Examples")
        st.table(df[df["sentiment_label"] == "positive"].head(5)[["text", "sentiment_polarity"]])
    with sub_col2:
        st.error("Negative Examples")
        st.table(df[df["sentiment_label"] == "negative"].head(5)[["text", "sentiment_polarity"]])

with tab3:
    st.markdown("### 📈 Engagement & Sentiment Correlation")
    if len(col_info["engagement"]) >= 2:
        eng_x = st.selectbox("X Axis (Engagement)", col_info["engagement"], index=0)
        eng_y = st.selectbox("Y Axis (Engagement)", col_info["engagement"], index=min(1, len(col_info["engagement"])-1))
        st.plotly_chart(viz.create_engagement_scatter(df, eng_x, eng_y), use_container_width=True)
    elif col_info["engagement"]:
        st.info(f"Only one engagement metric detected: {col_info['engagement'][0]}. Adding more metrics would enable scatter analysis.")
        st.plotly_chart(viz.create_category_bar(df, col_info["engagement"][0]), use_container_width=True)
    else:
        st.warning("No engagement metrics (Likes, Retweets, etc.) detected in this CSV.")

    st.markdown("---")
    st.markdown("### 🌡️ Time-based Sentiment Heatmap")
    heat_cat = st.selectbox("Heatmap Category", [c for c in col_info["categorical"] if c != "None"], key="heat_cat")
    if heat_cat:
        heat_fig = viz.create_sentiment_heatmap(df, heat_cat)
        if heat_fig:
            st.plotly_chart(heat_fig, use_container_width=True)
        else:
            st.info("Need an 'Hour' column or 'Timestamp' to generate the heatmap.")

with tab4:
    feed = RealTimeCSVFeed(df)
    feed.render()

# Footer Actions
st.markdown("---")
col_f1, col_f2 = st.columns(2)
with col_f1:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Export Analyzed Data", data=csv, file_name="analysis_export.csv", mime="text/csv")
with col_f2:
    if st.button("Clear Session Data"):
        del st.session_state.processed_df
        st.rerun()
