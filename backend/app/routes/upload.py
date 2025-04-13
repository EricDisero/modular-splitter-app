"""
File upload handling routes for audio files.
"""
import os
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.utils.minio_client import upload_file

router = APIRouter(prefix="/api", tags=["upload"])

# Allowed audio file extensions
ALLOWED_EXTENSIONS = [".aif", ".mp3", ".flac", ".wav"]


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file, store it in MinIO, and return metadata.

    Args:
        file: The uploaded audio file

    Returns:
        JSON response with file metadata
    """
    # Validate file extension
    filename = file.filename
    _, ext = os.path.splitext(filename.lower())

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Please upload {', '.join(ALLOWED_EXTENSIONS)} files."
        )

    # Determine content type
    content_type = "audio/mpeg"
    if ext == ".wav":
        content_type = "audio/wav"
    elif ext == ".flac":
        content_type = "audio/flac"
    elif ext == ".aif":
        content_type = "audio/aiff"

    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Check file size (limit to 500MB)
        if file_size > 500 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 500MB."
            )

        # Upload to MinIO
        object_name = await upload_file_to_minio(file_content, filename, content_type)
        if not object_name:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage."
            )

        # Return successful response with file details
        return {
            "success": True,
            "filename": filename,
            "object_name": object_name,
            "size": file_size,
            "content_type": content_type
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing upload: {str(e)}"
        )


async def upload_file_to_minio(file_content: bytes, filename: str, content_type: str) -> str:
    """
    Upload file to MinIO storage.

    Args:
        file_content: The file content as bytes
        filename: Original filename
        content_type: MIME type of the file

    Returns:
        The object name in MinIO
    """
    # Upload to MinIO
    object_name = upload_file(
        file_data=file_content,
        object_name=filename,  # Use original filename
        content_type=content_type
    )

    if not object_name:
        raise Exception("Failed to upload file to MinIO")

    return object_name