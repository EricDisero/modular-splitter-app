"""
Routes for handling audio splitting requests.
This module orchestrates requests between the frontend and the splitter service.
"""
import os
import json
import requests
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.minio_client import get_presigned_url

router = APIRouter(prefix="/api", tags=["split"])


@router.post("/split")
async def split_audio(background_tasks: BackgroundTasks, data: Dict[str, Any] = Body(...)):
    """
    Request audio splitting for a previously uploaded file.

    Args:
        background_tasks: FastAPI background tasks for async processing
        data: Request data containing file details

    Returns:
        JSON response with job status or error
    """
    object_name = data.get("object_name")
    if not object_name:
        raise HTTPException(
            status_code=400,
            detail="No file specified for splitting"
        )

    try:
        # Forward the request to the splitter service
        splitter_response = await request_splitting(object_name)

        # Return the job ID and status from the splitter service
        return {
            "success": True,
            "status": "processing",
            "job_id": splitter_response.get("job_id"),
            "message": "Audio splitting started successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initiating split: {str(e)}"
        )


@router.get("/split/{job_id}/status")
async def get_split_status(job_id: str):
    """
    Check the status of a splitting job.

    Args:
        job_id: The ID of the splitting job

    Returns:
        JSON response with job status and details
    """
    try:
        # Make request to splitter service to check status
        response = requests.get(
            f"{settings.SPLITTER_URL}/split/{job_id}/status",
            timeout=10
        )

        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={"success": False, "message": "Failed to get job status"}
            )

        # Get the response data
        data = response.json()

        # If the job is complete, add presigned URLs for the stems
        if data.get("status") == "completed":
            # Generate presigned URLs for each stem
            stems = data.get("stems", [])
            for i, stem in enumerate(stems):
                stem_object_name = stem.get("object_name")
                if stem_object_name:
                    stems[i]["download_url"] = get_presigned_url(stem_object_name)

        return data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking split status: {str(e)}"
        )


async def request_splitting(object_name: str) -> Dict[str, Any]:
    """
    Send a request to the splitter service to process an audio file.

    Args:
        object_name: The name of the audio file object in MinIO

    Returns:
        The response from the splitter service
    """
    try:
        # Prepare request data
        request_data = {
            "object_name": object_name,
            "bucket_name": settings.MINIO_BUCKET_NAME,
            "minio_endpoint": settings.MINIO_ENDPOINT,
            "minio_access_key": settings.MINIO_ACCESS_KEY,
            "minio_secret_key": settings.MINIO_SECRET_KEY,
            "minio_secure": settings.MINIO_SECURE
        }

        # Send request to splitter service
        response = requests.post(
            f"{settings.SPLITTER_URL}/split",
            json=request_data,
            timeout=30
        )

        if response.status_code != 200:
            error_message = f"Splitter service returned status {response.status_code}"
            try:
                error_message = response.json().get("detail", error_message)
            except:
                pass
            raise Exception(error_message)

        return response.json()

    except requests.RequestException as e:
        raise Exception(f"Error communicating with splitter service: {str(e)}")