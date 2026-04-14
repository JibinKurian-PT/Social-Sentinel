from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import uuid
import pandas as pd
from typing import Dict, Any, List
import logging
from src.tasks.csv_tasks import process_csv_upload_task
from src.api.middleware.auth import get_api_key

router = APIRouter(prefix="/csv", tags=["CSV Analysis"])
logger = logging.getLogger(__name__)

# Temporary storage for uploaded files and job status
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory status tracking (In production, use Redis/DB)
job_status = {}

@router.post("/upload")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    text_column: str = "text",
    model_type: str = "accurate",
    api_key: str = Depends(get_api_key)
):
    """
    Upload a CSV file and start sentiment analysis in the background.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")
        
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.csv")
    
    # Save file locally
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > 200 * 1024 * 1024: # 200MB limit
                raise HTTPException(status_code=413, detail="File too large (Max 200MB)")
            buffer.write(content)
    except Exception as e:
        logger.error(f"Failed to save upload: {e}")
        raise HTTPException(status_code=500, detail="File upload failed.")
        
    # Check if column exists
    try:
        df_preview = pd.read_csv(file_path, nrows=1)
        if text_column not in df_preview.columns:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found in CSV.")
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")

    # Start background task
    job_status[job_id] = {"status": "pending", "progress": 0, "message": "Queued for processing"}
    
    # In a real Celery setup, we'd use .delay()
    # For now, we use FastAPI background tasks or Celery if initialized
    process_csv_upload_task.delay(job_id, file_path, text_column, model_type)
    
    return {
        "job_id": job_id,
        "message": "Upload successful. Analysis started.",
        "status_url": f"/api/v1/csv/status/{job_id}"
    }

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Check the status of a CSV processing job."""
    # Note: In production, Celery result backend would handle this.
    # Here we simulate or pull from a shared state.
    from celery.result import AsyncResult
    result = AsyncResult(job_id)
    
    return {
        "job_id": job_id,
        "status": result.status,
        "progress": result.info.get("progress", 0) if isinstance(result.info, dict) else 0,
        "message": result.info.get("message", "") if isinstance(result.info, dict) else str(result.info)
    }

@router.get("/download/{job_id}")
async def download_results(job_id: str):
    """Download the analyzed CSV file."""
    output_path = os.path.join(UPLOAD_DIR, f"{job_id}_analyzed.csv")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Analyzed file not found or still processing.")
        
    return FileResponse(
        output_path, 
        media_type="text/csv", 
        filename=f"analyzed_results_{job_id}.csv"
    )

@router.get("/sample")
async def get_sample():
    """Download a sample CSV template."""
    sample_path = "data/raw/sample_data.csv"
    if not os.path.exists(sample_path):
        from scripts.create_sample_csv import generate_sample_csv
        generate_sample_csv(sample_path)
        
    return FileResponse(sample_path, media_type="text/csv", filename="sample_sentiment_template.csv")
