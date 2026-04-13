import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from src.dashboard.config import API_BASE_URL, COLOR_MAP, API_KEY
from src.dashboard.components.kpi_cards import render_kpi_row
from src.dashboard.components.charts import render_volume_bar_chart
from src.dashboard.utils import get_from_api, handle_api_error
import logging

logger = logging.getLogger(__name__)

st.title("System Overview & Aggregate Trends")

# Ensure sidebar components initialize session state
if "filter_time" not in st.session_state:
    st.session_state.filter_time = "Last 24 Hours"

def parse_hours(time_str: str) -> int:
    if "1 Hour" in time_str: return 1
    if "7 Days" in time_str: return 24 * 7
    if "30 Days" in time_str: return 24 * 30
    return 24

# Fetch Data with Retry Logic
@st.cache_data(ttl=60)
def fetch_trends_data(hours: int):
    try:
        data = get_from_api(f"{API_BASE_URL}/trends/hourly", headers={"X-API-Key": API_KEY})
        return data.get("aggregates", [])
    except Exception as e:
        handle_api_error(e, "fetching trends data")
        return []

try:
    time_h = parse_hours(st.session_state.filter_time)
    data = fetch_trends_data(time_h)

    if not data:
        st.warning("No data available for the selected time range. Please ensure the system is seeded.")
    else:
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate top level KPIs
        total_pos = df['positive_count'].sum()
        total_neg = df['negative_count'].sum()
        total_neu = df['neutral_count'].sum()
        total = total_pos + total_neg + total_neu
        
        pos_pct = (total_pos / total * 100) if total > 0 else 0
        neg_pct = (total_neg / total * 100) if total > 0 else 0
        
        # Render KPIs
        render_kpi_row(total, pos_pct, neg_pct, active_topics=5) 
        st.markdown("---")
        
        # Time Series Area Chart
        st.subheader("Sentiment Distribution Over Time")
        
        # Prepare data for stacked area chart
        time_grouped = df.groupby('date')[['positive_count', 'negative_count', 'neutral_count']].sum().reset_index()
        time_melted = pd.melt(
            time_grouped, 
            id_vars=['date'], 
            value_vars=['positive_count', 'neutral_count', 'negative_count'],
            var_name='Sentiment', value_name='Volume'
        )
        time_melted['Sentiment'] = time_melted['Sentiment'].map({
            'positive_count': 'Positive', 
            'neutral_count': 'Neutral', 
            'negative_count': 'Negative'
        })
        
        fig_area = px.area(
            time_melted, 
            x="date", y="Volume", color="Sentiment",
            color_discrete_map=COLOR_MAP,
            template="plotly_dark",
            title="Aggregate Volume by Sentiment Label"
        )
        st.plotly_chart(fig_area, use_container_width=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total Volume by Platform")
            # Map platform names to colors if needed
            fig_bar = px.bar(
                df.groupby('platform')['positive_count'].sum().reset_index(), 
                x='platform', y='positive_count',
                labels={'positive_count': 'Total Volume'},
                template="plotly_dark"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            st.subheader("Average Polarity Score")
            polarity_trend = df.groupby('date')['avg_polarity'].mean().reset_index()
            fig_line = px.line(
                polarity_trend, 
                x="date", y="avg_polarity", 
                template="plotly_dark",
                markers=True
            )
            fig_line.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_line.update_layout(yaxis_range=[-1.0, 1.0])
            st.plotly_chart(fig_line, use_container_width=True)

except Exception as e:
    st.error(f"A critical error occurred while rendering the page: {e}")
    logger.exception("Overview page crash")
