from celery import shared_task
import logging
import os
import asyncio
from src.csv_processor.batch_sentiment_analyzer import BatchSentimentAnalyzer

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_csv_upload_task(self, job_id: str, file_path: str, text_column: str, model_type: str):
    """
    Celery task to process a CSV file in the background.
    """
    logger.info(f"Starting Celery task for job {job_id}")
    self.update_state(state="PROGRESS", meta={"progress": 0, "message": "Initializing analyzer..."})
    
    try:
        # Create a callback to update Celery state
        def progress_callback(progress, message):
            self.update_state(state="PROGRESS", meta={
                "progress": int(progress * 100),
                "message": message
            })
            
        # Initialize analyzer
        analyzer = BatchSentimentAnalyzer(model_type=model_type)
        
        # We need an event loop for the async processing
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run processing
        results_df = loop.run_until_complete(
            analyzer.process_csv_file(
                file_path=file_path,
                text_column=text_column,
                batch_size=100,
                callback=progress_callback
            )
        )
        
        # Save analyzed results back to disk for easy download
        output_path = file_path.replace(".csv", "_analyzed.csv")
        results_df.to_csv(output_path, index=False)
        
        logger.info(f"Job {job_id} complete. Output saved to {output_path}")
        
        return {
            "status": "completed",
            "progress": 100,
            "message": "Analysis finished successfully.",
            "output_path": output_path
        }
        
    except Exception as e:
        logger.error(f"Error in job {job_id}: {e}")
        self.update_state(state="FAILURE", meta={
            "progress": 0,
            "message": f"Error: {str(e)}"
        })
        raise e

@shared_task
def cleanup_old_csv_files_task(days: int = 7):
    """
    Periodic task to clean up old uploaded and analyzed files.
    """
    import time
    UPLOAD_DIR = "data/uploads"
    if not os.path.exists(UPLOAD_DIR):
        return
        
    now = time.time()
    cutoff = now - (days * 86400)
    
    count = 0
    for f in os.listdir(UPLOAD_DIR):
        f_path = os.path.join(UPLOAD_DIR, f)
        if os.path.getmtime(f_path) < cutoff:
            os.remove(f_path)
            count += 1
            
    logger.info(f"Cleaned up {count} old CSV files.")
    return f"Removed {count} files"
