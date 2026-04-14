import streamlit as st
import pandas as pd
import os
import requests
from typing import Optional, Tuple, List

class CSVUploadComponent:
    """
    Reusable UI component for CSV file uploading and column selection.
    """
    
    def __init__(self, api_url: str = "http://localhost:8000/api/v1"):
        self.api_url = api_url

    def render(self) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Renders the uploader and returns the DataFrame and selected text column."""
        
        st.markdown("### 📥 Step 1: Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV file (Max 200MB)", 
            type="csv",
            help="Supported: UTF-8, CSV only."
        )
        
        if uploaded_file is not None:
            try:
                # Read a small sample first for preview
                sample_df = pd.read_csv(uploaded_file, nrows=100)
                uploaded_file.seek(0) # Reset pointer
                
                st.success(f"✅ Loaded: {uploaded_file.name} ({len(sample_df)} rows previewed)")
                
                # Column Selection
                st.markdown("### 🔍 Step 2: Configure Columns")
                cols = list(sample_df.columns)
                
                # Try to auto-detect text column
                default_text_idx = 0
                for i, col in enumerate(cols):
                    if "text" in col.lower() or "content" in col.lower() or "tweet" in col.lower():
                        default_text_idx = i
                        break
                
                text_col = st.selectbox(
                    "Which column contains the text to analyze?",
                    options=cols,
                    index=default_text_idx
                )
                
                with st.expander("Preview data"):
                    st.dataframe(sample_df.head(5))
                
                return uploaded_file, text_col
                
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
                return None, None
                
        return None, None

    def render_processing_options(self) -> dict:
        """Renders the settings for analysis."""
        st.markdown("### ⚙️ Step 3: Analysis Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            model = st.selectbox(
                "Sentiment Model",
                options=["Accurate Mode (BERT Ensemble)", "Fast Mode (TextBlob)"],
                index=0,
                help="Accurate Mode uses a deep learning BERT ensemble (Slower). Fast Mode uses rule-based logic (Instant)."
            )
        with col2:
            batch_size = st.slider("Batch Size", 10, 500, 100, help="How many rows to process at once.")
            
        return {
            "model_type": "accurate" if "Accurate" in model else "fast",
            "batch_size": batch_size
        }

    def download_results_buttons(self, df: pd.DataFrame, job_id: str):
        """Renders download buttons for the analyzed results."""
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        csv = df.to_csv(index=False).encode('utf-8')
        
        with col1:
            st.download_button(
                label="📥 Download Analyzed CSV",
                data=csv,
                file_name=f"sentiment_results_{job_id}.csv",
                mime='text/csv',
                use_container_width=True
            )
        
        with col2:
            if st.button("📊 Open Visual Dashboard", use_container_width=True):
                st.session_state.processed_df = df
                st.session_state.current_job_id = job_id
                # In Streamlit, we'd typically use st.switch_page if available
                st.info("Navigate to 'CSV Dashboard' in the sidebar to view full analytics!")
