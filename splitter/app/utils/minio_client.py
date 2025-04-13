"""
MinIO client utilities for the splitter service.
"""
import os
import logging
from io import BytesIO
import tempfile
import uuid
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger("splitter.minio")


class MinioClient:
    """
    MinIO client for handling file storage.
    """

    def __init__(
            self,
            endpoint,
            access_key,
            secret_key,
            bucket_name="stems",
            secure=False
    ):
        """
        Initialize MinIO client.

        Args:
            endpoint: MinIO server endpoint
            access_key: MinIO access key
            secret_key: MinIO secret key
            bucket_name: Bucket name for storing files
            secure: Use secure connection
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.secure = secure

        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

        # Ensure bucket exists
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self):
        """
        Ensure that the bucket exists, creating it if needed.
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' created successfully")
            return True
        except S3Error as err:
            logger.error(f"Error ensuring bucket exists: {err}")
            return False

    def download_file(self, object_name, output_path=None):
        """
        Download a file from MinIO.

        Args:
            object_name: The name of the object in the bucket
            output_path: Path to save the file (optional)

        Returns:
            Path to the downloaded file or None if failed
        """
        try:
            # If no output path specified, create a temporary file
            if output_path is None:
                ext = os.path.splitext(object_name)[1] or ".tmp"
                output_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                output_path = output_file.name
                output_file.close()

            # Download the file
            self.client.fget_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=output_path
            )

            logger.info(f"Downloaded {object_name} to {output_path}")
            return output_path
        except S3Error as err:
            logger.error(f"Error downloading file from MinIO: {err}")
            return None

    def upload_file(self, file_path, object_name=None, content_type=None):
        """
        Upload a file to MinIO.

        Args:
            file_path: Path to the file to upload
            object_name: Name to use for the object (optional)
            content_type: Content type of the file (optional)

        Returns:
            The object name if successful, None otherwise
        """
        try:
            # Determine object name if not provided
            if object_name is None:
                _, ext = os.path.splitext(file_path)
                object_name = f"{uuid.uuid4().hex}{ext}"

            # Determine content type if not provided
            if content_type is None:
                # Guess content type based on extension
                ext = os.path.splitext(file_path)[1].lower()
                if ext == ".wav":
                    content_type = "audio/wav"
                elif ext == ".mp3":
                    content_type = "audio/mpeg"
                elif ext == ".flac":
                    content_type = "audio/flac"
                else:
                    content_type = "application/octet-stream"

            # Upload file
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )

            logger.info(f"Uploaded {file_path} to MinIO as {object_name}")
            return object_name
        except S3Error as err:
            logger.error(f"Error uploading file to MinIO: {err}")
            return None

    def upload_bytes(self, data, object_name, content_type="application/octet-stream"):
        """
        Upload bytes data to MinIO.

        Args:
            data: Bytes data to upload
            object_name: Name to use for the object
            content_type: Content type of the data

        Returns:
            The object name if successful, None otherwise
        """
        try:
            # Create BytesIO object
            data_stream = BytesIO(data)
            file_size = len(data)

            # Upload data
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=file_size,
                content_type=content_type
            )

            logger.info(f"Uploaded {len(data)} bytes to MinIO as {object_name}")
            return object_name
        except S3Error as err:
            logger.error(f"Error uploading bytes to MinIO: {err}")
            return None

    def delete_file(self, object_name):
        """
        Delete a file from MinIO.

        Args:
            object_name: Name of the object to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )

            logger.info(f"Deleted {object_name} from MinIO")
            return True
        except S3Error as err:
            logger.error(f"Error deleting file from MinIO: {err}")
            return False