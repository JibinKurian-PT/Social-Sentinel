import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List, Any, Optional

class VisualizationGenerator:
    """
    Automatically generates professional Plotly visualizations from analyzed DataFrames.
    """
    
    @staticmethod
    def detect_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
        """Identifies text, date, numeric, and categorical columns in the dataset."""
        types = {
            "text": [],
            "date": [],
            "numeric": [],
            "categorical": [],
            "engagement": [],
            "geo": []
        }
        
        engagement_keywords = ["likes", "retweets", "shares", "reactions", "comments", "engagement"]
        geo_keywords = ["country", "location", "city", "state", "lat", "lon", "geo"]
        
        for col in df.columns:
            low_col = col.lower()
            
            # Check for engagement
            if any(k in low_col for k in engagement_keywords) and pd.api.types.is_numeric_dtype(df[col]):
                types["engagement"].append(col)
                types["numeric"].append(col)
                continue

            # Check for geo
            if any(k in low_col for k in geo_keywords):
                types["geo"].append(col)
                types["categorical"].append(col)
                continue

            # Check for date
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                types["date"].append(col)
            elif "date" in low_col or "time" in low_col or "timestamp" in low_col:
                try:
                    pd.to_datetime(df[col].head(10))
                    types["date"].append(col)
                except:
                    pass
            
            # Check for numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].nunique() > 10: # Likely continuous numeric
                    types["numeric"].append(col)
                else:
                    types["categorical"].append(col)
            
            # Check for categorical
            elif df[col].nunique() < 30: # Increased threshold for platforms/countries
                types["categorical"].append(col)
            
            # Check for text
            elif pd.api.types.is_string_dtype(df[col]):
                avg_len = df[col].str.len().mean()
                if avg_len > 20:
                    types["text"].append(col)
                    
        return types

    def create_sentiment_pie(self, df: pd.DataFrame) -> go.Figure:
        """Creates a primary pie chart for sentiment distribution."""
        counts = df["sentiment_label"].value_counts().reset_index()
        counts.columns = ["Sentiment", "Count"]
        
        colors = {
            "positive": "#00CC96",
            "negative": "#EF553B",
            "neutral": "#AB63FA"
        }
        
        fig = px.pie(
            counts, 
            values="Count", 
            names="Sentiment",
            color="Sentiment",
            color_discrete_map=colors,
            hole=0.4,
            title="Overall Sentiment Distribution"
        )
        fig.update_layout(
            showlegend=True, 
            margin=dict(t=60, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    def create_polarity_histogram(self, df: pd.DataFrame) -> go.Figure:
        """Creates a histogram of polarity scores."""
        fig = px.histogram(
            df, 
            x="sentiment_polarity",
            color="sentiment_label",
            nbins=50,
            title="Sentiment Intensity distribution",
            labels={"sentiment_polarity": "Polarity Score (-1 to 1)"},
            color_discrete_map={"positive": "#00CC96", "negative": "#EF553B", "neutral": "#AB63FA"},
            marginal="box" # Changed to box for better statistical view
        )
        fig.update_layout(bargap=0.1, margin=dict(t=60))
        return fig

    def create_engagement_scatter(self, df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
        """Creates a scatter plot for engagement metrics by sentiment."""
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col, 
            color="sentiment_label",
            size=df[x_col].abs() + 1, # Bubble size based on engagement
            hover_data=["text"] if "text" in df.columns else None,
            title=f"Engagement Analysis: {y_col} vs {x_col}",
            color_discrete_map={"positive": "#00CC96", "negative": "#EF553B", "neutral": "#AB63FA"},
            marginal_x="histogram",
            marginal_y="violin",
            template="plotly_dark"
        )
        fig.update_layout(margin=dict(t=60))
        return fig

    def create_sentiment_heatmap(self, df: pd.DataFrame, x_cat: str) -> go.Figure:
        """Creates a heatmap of sentiment averages by category and hour of day."""
        df_copy = df.copy()
        
        # Check for hour column or try to extract from date
        hour_col = None
        if "Hour" in df_copy.columns:
            hour_col = "Hour"
        else:
            date_cols = [c for c in df_copy.columns if pd.api.types.is_datetime64_any_dtype(df_copy[c])]
            if date_cols:
                df_copy["generated_hour"] = df_copy[date_cols[0]].dt.hour
                hour_col = "generated_hour"
        
        if hour_col and x_cat:
            pivot = df_copy.pivot_table(
                index=x_cat, 
                columns=hour_col, 
                values="sentiment_polarity", 
                aggfunc="mean"
            ).fillna(0)
            
            fig = px.imshow(
                pivot,
                labels=dict(x="Hour of Day", y=x_cat, color="Avg Polarity"),
                x=pivot.columns,
                y=pivot.index,
                title=f"Sentiment Heatmap: {x_cat} vs Hour",
                color_continuous_scale="RdYlGn",
                aspect="auto"
            )
            return fig
        return None

    def create_trend_chart(self, df: pd.DataFrame, date_col: str) -> go.Figure:
        """Creates a line chart for sentiment over time."""
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        
        # Resample by day or hour depending on span
        time_span = df_copy[date_col].max() - df_copy[date_col].min()
        freq = "D" if time_span.days > 2 else "H"
        
        trend = df_copy.groupby([pd.Grouper(key=date_col, freq=freq), "sentiment_label"]).size().unstack(fill_value=0)
        
        fig = px.line(
            trend, 
            title=f"Sentiment Trend Over Time ({'Daily' if freq=='D' else 'Hourly'})",
            color_discrete_map={"positive": "#00CC96", "negative": "#EF553B", "neutral": "#AB63FA"}
        )
        fig.update_layout(xaxis_title="Time", yaxis_title="Number of Posts")
        return fig

    def create_category_bar(self, df: pd.DataFrame, cat_col: str) -> go.Figure:
        """Creates a stacked bar chart showing sentiment by category."""
        cat_data = df.groupby([cat_col, "sentiment_label"]).size().reset_index(name="count")
        
        fig = px.bar(
            cat_data, 
            x=cat_col, 
            y="count", 
            color="sentiment_label",
            title=f"Sentiment Breakdown by {cat_col}",
            barmode="stack",
            color_discrete_map={"positive": "#00CC96", "negative": "#EF553B", "neutral": "#AB63FA"}
        )
        return fig

    def create_wordcloud_base64(self, df: pd.DataFrame, text_col: str) -> str:
        """Generates a word cloud and returns it as a base64 string for Streamlit."""
        text = " ".join(df[text_col].astype(str).tolist())
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color="#1e1e1e",
            colormap="viridis",
            max_words=100
        ).generate(text)
        
        img = io.BytesIO()
        wordcloud.to_image().save(img, format="PNG")
        return base64.b64encode(img.getvalue()).decode()

    def create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Creates a heatmap for numerical correlations."""
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return None
            
        corr = numeric_df.corr()
        fig = px.imshow(
            corr, 
            text_auto=True, 
            aspect="auto",
            title="Feature Correlation Matrix",
            color_continuous_scale="RdBu_r"
        )
        return fig
