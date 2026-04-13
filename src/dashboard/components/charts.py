import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import pandas as pd # type: ignore
from src.dashboard.config import COLOR_MAP, PLATFORM_COLORS

def render_sentiment_pie_chart(data: pd.DataFrame, label_col: str = "label"):
    """Render a standard sentiment distribution pie chart."""
    counts = data[label_col].value_counts().reset_index()
    counts.columns = ['label', 'count']
    
    # Capitalize for dictionary mapping
    counts['label'] = counts['label'].str.capitalize()
    
    fig = px.pie(
        counts, 
        values='count', 
        names='label',
        color='label',
        color_discrete_map=COLOR_MAP,
        hole=0.4
    )
    fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), template="plotly_dark")
    return fig

def render_volume_bar_chart(data: pd.DataFrame, time_col: str, vol_col: str, group_col: str):
    """Render a stacked bar chart for aggregate volume over time."""
    fig = px.bar(
        data,
        x=time_col,
        y=vol_col,
        color=group_col,
        color_discrete_map=PLATFORM_COLORS,
        barmode='stack',
        template="plotly_dark"
    )
    fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), xaxis_title="")
    return fig
