"""
Routes for audio splitting with HTDemucs.
"""
import os
import logging
import json
import shutil
import asyncio
import time
from typing import Dict, Any
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException, Body

from app.models.demucs_runner import HTDemucsRunner
from app.models.stems_processor import StemsProcessor
from app.utils.minio_client import MinioClient
from app.utils.audio import cleanup_temp_files

router = APIRouter(tags=["split"])

# Configure logging
logger = logging.getLogger("splitter.routes")

# In-memory job store for tracking splitting jobs
jobs = {}


@router.post("/split")
async def split_audio(background_tasks: BackgroundTasks, data: Dict[str, Any] = Body(...)):
    """
    Split audio into stems using HTDemucs.

    Args:
        background_tasks: FastAPI background tasks for async processing
        data: Request data containing file details and MinIO connection info

    Returns:
        JSON response with job ID and initial status
    """
    try:
        # Extract MinIO configuration from request
        minio_config = {
            "endpoint": data.get("minio_endpoint"),
            "access_key": data.get("minio_access_key"),
            "secret_key": data.get("minio_secret_key"),
            "bucket_name": data.get("bucket_name", "stems"),
            "secure": data.get("minio_secure", False)
        }

        # Extract file details
        object_name = data.get("object_name")
        if not object_name:
            raise HTTPException(status_code=400, detail="No file specified for splitting")

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Initialize job status
        jobs[job_id] = {
            "status": "queued",
            "object_name": object_name,
            "created_at": time.time(),
            "updated_at": time.time(),
            "minio_config": minio_config,
            "progress": 0,
            "stems": []
        }

        # Start background process
        background_tasks.add_task(
            process_audio_splitting,
            job_id,
            object_name,
            minio_config
        )

        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Audio splitting job queued successfully"
        }

    except Exception as e:
        logger.error(f"Error initiating split: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating split: {str(e)}")


@router.get("/split/{job_id}/status")
async def get_split_status(job_id: str):
    """
    Get the status of a splitting job.

    Args:
        job_id: The ID of the splitting job

    Returns:
        JSON response with job status and details
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")

    # Return job status
    return jobs[job_id]


async def process_audio_splitting(job_id: str, object_name: str, minio_config: Dict[str, Any]):
    """
    Process audio splitting in the background.

    Args:
        job_id: The ID of the splitting job
        object_name: Name of the object in MinIO
        minio_config: MinIO configuration
    """
    temp_files = []

    try:
        # Update job status
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 5
        jobs[job_id]["updated_at"] = time.time()

        # Connect to MinIO
        minio_client = MinioClient(
            endpoint=minio_config["endpoint"],
            access_key=minio_config["access_key"],
            secret_key=minio_config["secret_key"],
            bucket_name=minio_config["bucket_name"],
            secure=minio_config["secure"]
        )

        # Download the file from MinIO
        jobs[job_id]["progress"] = 10
        jobs[job_id]["updated_at"] = time.time()

        local_file_path = minio_client.download_file(object_name)
        if not local_file_path:
            raise Exception(f"Failed to download file {object_name} from MinIO")

        temp_files.append(local_file_path)

        # Update job status
        jobs[job_id]["progress"] = 20
        jobs[job_id]["updated_at"] = time.time()

        # Initialize HTDemucs runner
        demucs_runner = HTDemucsRunner(
            model_name="htdemucs",
            device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") is not None else "cpu",
            shifts=1,
            split=True,
            overlap=0.25,
            float32=True
        )

        # Separate stems
        jobs[job_id]["progress"] = 30
        jobs[job_id]["updated_at"] = time.time()

        # Get original filename without extension for output naming
        original_filename = os.path.splitext(os.path.basename(object_name))[0]

        # Run HTDemucs
        logger.info(f"Starting HTDemucs processing for job {job_id}")
        stem_files = demucs_runner.separate(local_file_path, filename_prefix=original_filename)

        if not stem_files:
            raise Exception("Stem separation failed")

        # Update job status
        jobs[job_id]["progress"] = 70
        jobs[job_id]["updated_at"] = time.time()

        # Process stems (adjust volume, create EE track, etc.)
        logger.info(f"Processing stems for job {job_id}")
        stems_processor = StemsProcessor()
        processed_result = stems_processor.process_stems(
            local_file_path,
            stem_files,
            output_prefix=original_filename
        )

        if not processed_result:
            raise Exception("Stem processing failed")

        # Update job status
        jobs[job_id]["progress"] = 80
        jobs[job_id]["updated_at"] = time.time()

        # Upload processed stems to MinIO
        logger.info(f"Uploading processed stems for job {job_id}")
        stem_outputs = []

        for stem_name, stem_path in processed_result["stems"].items():
            # Upload to MinIO
            stem_object_name = f"{original_filename}/{os.path.basename(stem_path)}"
            uploaded_object = minio_client.upload_file(stem_path, stem_object_name)

            if uploaded_object:
                stem_outputs.append({
                    "stem_name": stem_name,
                    "object_name": uploaded_object,
                    "filename": os.path.basename(stem_path)
                })

        # Create and upload ZIP package
        zip_path = stems_processor.create_zip_package(processed_result["output_dir"])
        if zip_path:
            zip_object_name = f"{original_filename}_stems.zip"
            uploaded_zip = minio_client.upload_file(zip_path, zip_object_name)

            if uploaded_zip:
                # Add ZIP to stems list
                stem_outputs.append({
                    "stem_name": "zip",
                    "object_name": uploaded_zip,
                    "filename": os.path.basename(zip_path)
                })

        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["updated_at"] = time.time()
        jobs[job_id]["stems"] = stem_outputs

        logger.info(f"Audio splitting completed for job {job_id}")

    except Exception as e:
        logger.error(f"Error processing audio splitting for job {job_id}: {str(e)}")

        # Update job status
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["updated_at"] = time.time()

    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files)

        # Clean up jobs older than 24 hours
        clean_old_jobs()


def clean_old_jobs():
    """
    Clean up jobs older than 24 hours.
    """
    current_time = time.time()
    job_ids_to_remove = []

    for job_id, job_info in jobs.items():
        # Keep jobs for 24 hours
        if current_time - job_info.get("created_at", current_time) > 86400:
            job_ids_to_remove.append(job_id)

    for job_id in job_ids_to_remove:
        try:
            del jobs[job_id]
            logger.info(f"Cleaned up old job {job_id}")
        except KeyError:
            pass