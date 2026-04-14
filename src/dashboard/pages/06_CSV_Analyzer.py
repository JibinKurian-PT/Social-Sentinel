import streamlit as st
import pandas as pd
import time
import os
import requests
from src.dashboard.components.csv_upload_component import CSVUploadComponent
from src.dashboard.config import setup_page
from src.csv_processor.batch_sentiment_analyzer import BatchSentimentAnalyzer
import asyncio

# Page Configuration
setup_page("CSV Sentiment Analyzer", "📥")

# Load Custom CSS
with open("static/custom_csv_style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📥 CSV Sentiment Analyzer")
st.markdown("""
Upload any CSV file (Twitter data, reviews, surveys) and get instant sentiment analysis. 
This tool uses state-of-the-art NLP to categorize every row into Positive, Negative, or Neutral.
""")

# Initialize Component
uploader = CSVUploadComponent()

# Page Layout
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    file, text_col = uploader.render()
    
    if file and text_col:
        options = uploader.render_processing_options()
        
        if st.button("🚀 Start Analysis", key="start_analysis"):
            # Save file temporarily for processing
            os.makedirs("data/uploads", exist_ok=True)
            temp_path = f"data/uploads/manual_{int(time.time())}.csv"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            
            # Processing Container
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Callback to update UI
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.markdown(f"**Status:** {message}")

            # Run analyzer
            analyzer = BatchSentimentAnalyzer(model_type=options["model_type"])
            
            try:
                start_time = time.time()
                # Use asyncio run since we're in a synchronous Streamlit script
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                df_results = loop.run_until_complete(
                    analyzer.process_csv_file(
                        file_path=temp_path,
                        text_column=text_col,
                        batch_size=options["batch_size"],
                        callback=update_progress
                    )
                )
                duration = time.time() - start_time
                
                st.success(f"🎊 Analysis Complete! Processed {len(df_results)} rows in {duration:.2f} seconds.")
                
                # Store in session state for the Dashboard page
                st.session_state.processed_df = df_results
                st.session_state.analysis_complete = True
                
                # Show results summary
                stats = analyzer.generate_summary_statistics(df_results)
                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", stats["total_rows"])
                c2.metric("Positive %", f"{(stats['positive']/stats['total_rows'])*100:.1f}%")
                c3.metric("Negative %", f"{(stats['negative']/stats['total_rows'])*100:.1f}%")
                
                # Download Options
                uploader.download_results_buttons(df_results, "manual_job")
                
            except Exception as e:
                st.error(f"Processing failed: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

with col_sidebar:
    st.image("https://img.icons8.com/clouds/200/csv.png", width=150)
    st.info("💡 **Tip:** Make sure your CSV file is UTF-8 encoded for best results.")
    
    st.markdown("### Sample Data")
    st.write("Don't have a CSV? Download our sample airline data to try it out.")
    if st.button("📥 Download Sample CSV", use_container_width=True):
        # Triggering internal generation
        from scripts.create_sample_csv import generate_sample_csv
        sample_path = "data/raw/sample_data.csv"
        generate_sample_csv(sample_path)
        with open(sample_path, "rb") as f:
            st.download_button(
                label="Click here to save sample.csv",
                data=f,
                file_name="sentiment_sample.csv"
            )
    
    st.markdown("---")
    st.markdown("### Why use Accurate Mode?")
    st.write("""
    **Accurate Mode** uses an ensemble of BERT models. It understands context, sarcasm, and complex sentences 
    far better than standard keyword matching. 
    """)
