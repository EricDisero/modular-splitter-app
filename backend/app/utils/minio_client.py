"""
MinIO client utilities for handling file storage.
"""
import os
from io import BytesIO
from datetime import timedelta
import uuid
from minio import Minio
from minio.error import S3Error

from app.config import settings

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)


def ensure_bucket_exists():
    """
    Ensure that the stems bucket exists, creating it if needed.
    """
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            print(f"Bucket '{settings.MINIO_BUCKET_NAME}' created successfully.")
        return True
    except S3Error as err:
        print(f"Error ensuring bucket exists: {err}")
        return False


def upload_file(file_data: bytes, object_name: str = None, content_type: str = "audio/mpeg"):
    """
    Upload a file to MinIO.

    Args:
        file_data: The file data as bytes
        object_name: The name to use for the object in the bucket
                     If None, a UUID will be generated
        content_type: The content type of the file

    Returns:
        The object name if successful, None otherwise
    """
    try:
        # Ensure bucket exists
        ensure_bucket_exists()

        # Generate object name if not provided
        if object_name is None:
            extension = "mp3"  # Default extension
            if content_type == "audio/wav":
                extension = "wav"
            elif content_type == "audio/flac":
                extension = "flac"
            object_name = f"{uuid.uuid4()}.{extension}"

        # Upload the file
        file_size = len(file_data)
        file_data_stream = BytesIO(file_data)

        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=object_name,
            data=file_data_stream,
            length=file_size,
            content_type=content_type
        )

        print(f"Uploaded {object_name} to MinIO")
        return object_name
    except S3Error as err:
        print(f"Error uploading file to MinIO: {err}")
        return None


def get_presigned_url(object_name: str, expires: int = 3600):
    """
    Generate a presigned URL for downloading an object.

    Args:
        object_name: The name of the object in the bucket
        expires: Expiry time in seconds (default: 1 hour)

    Returns:
        The presigned URL if successful, None otherwise
    """
    try:
        url = minio_client.presigned_get_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=object_name,
            expires=timedelta(seconds=expires)
        )
        return url
    except S3Error as err:
        print(f"Error generating presigned URL: {err}")
        return None


def delete_file(object_name: str):
    """
    Delete a file from MinIO.

    Args:
        object_name: The name of the object to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        minio_client.remove_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=object_name
        )
        return True
    except S3Error as err:
        print(f"Error deleting file from MinIO: {err}")
        return False