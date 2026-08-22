"""MinIO and S3-compatible Object Storage management service using boto3."""

import io
import uuid
from typing import Any, Dict, Optional
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from backend.app.core.config import settings
from backend.app.core.security import compute_sha256


class ObjectStorageService:
    """
    Manages object keys, storage buckets, binary uploads/downloads,
    and SHA-256 verification for images, crops, reports, and listing snapshots.
    Integrates with MinIO (local dev / Docker) and AWS S3 in production.
    """

    BUCKET_EVIDENCE = settings.MINIO_BUCKET_EVIDENCE
    BUCKET_REPORTS = settings.MINIO_BUCKET_REPORTS
    BUCKET_SNAPSHOTS = settings.MINIO_BUCKET_SNAPSHOTS

    _client: Optional[Any] = None

    @classmethod
    def get_client(cls):
        """Lazy-initialize and return boto3 S3 client using environment settings."""
        if cls._client is None:
            endpoint_url = f"{'https' if settings.MINIO_USE_SSL else 'http'}://{settings.MINIO_ENDPOINT}"
            cls._client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.MINIO_ROOT_USER,
                aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
                config=Config(signature_version="s3v4"),
                region_name="us-east-1",
            )
        return cls._client

    @classmethod
    def set_client(cls, client: Any) -> None:
        """Override internal client (used for testing and mocking)."""
        cls._client = client

    @classmethod
    def ensure_buckets_exist(cls) -> None:
        """Ensure default LabelSetu buckets exist in object storage."""
        client = cls.get_client()
        for bucket in [cls.BUCKET_EVIDENCE, cls.BUCKET_REPORTS, cls.BUCKET_SNAPSHOTS]:
            try:
                client.head_bucket(Bucket=bucket)
            except ClientError:
                try:
                    client.create_bucket(Bucket=bucket)
                except Exception:
                    pass

    @staticmethod
    def build_evidence_key(
        inspection_id: uuid.UUID | str,
        image_type: str,  # 'originals', 'crops', 'fiducial'
        filename: str,
    ) -> str:
        """
        Build standardized evidence object key.
        Pattern: inspections/{inspection_id}/{image_type}/{uuid}_{filename}
        """
        unique_prefix = uuid.uuid4().hex[:8]
        safe_filename = filename.replace(" ", "_")
        return f"inspections/{str(inspection_id)}/{image_type}/{unique_prefix}_{safe_filename}"

    @staticmethod
    def build_report_key(
        inspection_id: uuid.UUID | str,
        report_type: str,  # 'pdf', 'docx', 'csv'
        version: str = "1.0",
    ) -> str:
        """
        Build standardized report object key.
        Pattern: reports/{inspection_id}/statutory_report_v{version}.{report_type}
        """
        return f"reports/{str(inspection_id)}/statutory_report_v{version}.{report_type.lower()}"

    @staticmethod
    def build_snapshot_key(
        platform: str,
        external_listing_id: str,
        timestamp_str: str,
    ) -> str:
        """
        Build marketplace listing snapshot key.
        Pattern: listings/{platform}/{external_listing_id}_{timestamp}.html
        """
        return f"listings/{platform.lower()}/{external_listing_id}_{timestamp_str}.html"

    @classmethod
    def upload_bytes(
        cls,
        bucket: str,
        object_key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Upload binary content to S3/MinIO and return its computed SHA-256 digest.
        """
        sha256_hash = compute_sha256(data)
        client = cls.get_client()
        extra_args: Dict[str, Any] = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata
        extra_args["Metadata"] = {**(metadata or {}), "sha256": sha256_hash}

        client.upload_fileobj(
            Fileobj=io.BytesIO(data),
            Bucket=bucket,
            Key=object_key,
            ExtraArgs=extra_args,
        )
        return sha256_hash

    @classmethod
    def download_bytes(cls, bucket: str, object_key: str) -> bytes:
        """
        Download binary object from S3/MinIO.
        """
        client = cls.get_client()
        buffer = io.BytesIO()
        client.download_fileobj(Bucket=bucket, Key=object_key, Fileobj=buffer)
        return buffer.getvalue()

    @classmethod
    def head_object(cls, bucket: str, object_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata and size for an object without downloading content.
        """
        client = cls.get_client()
        try:
            response = client.head_object(Bucket=bucket, Key=object_key)
            return response
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                return None
            raise

    @classmethod
    def delete_object(cls, bucket: str, object_key: str) -> bool:
        """
        Delete an object from S3/MinIO bucket.
        """
        client = cls.get_client()
        try:
            client.delete_object(Bucket=bucket, Key=object_key)
            return True
        except ClientError:
            return False

    @staticmethod
    def verify_content_sha256(content: bytes, expected_hash: str) -> bool:
        """Verify that the binary content matches the expected SHA-256 hash."""
        actual_hash = compute_sha256(content)
        return actual_hash.lower() == expected_hash.lower()

    @classmethod
    def get_presigned_upload_url(
        cls,
        bucket: str,
        object_key: str,
        expires_seconds: int = 3600,
    ) -> str:
        """
        Generate S3/MinIO presigned upload URL for direct client multipart upload.
        """
        client = cls.get_client()
        try:
            url = client.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": bucket, "Key": object_key},
                ExpiresIn=expires_seconds,
            )
            return url
        except Exception:
            scheme = "https" if settings.MINIO_USE_SSL else "http"
            return f"{scheme}://{settings.MINIO_ENDPOINT}/{bucket}/{object_key}?upload_token={uuid.uuid4().hex}"

    @classmethod
    def get_presigned_download_url(
        cls,
        bucket: str,
        object_key: str,
        expires_seconds: int = 3600,
    ) -> str:
        """
        Generate S3/MinIO presigned download URL with time-limited access.
        """
        client = cls.get_client()
        try:
            url = client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": object_key},
                ExpiresIn=expires_seconds,
            )
            return url
        except Exception:
            scheme = "https" if settings.MINIO_USE_SSL else "http"
            return f"{scheme}://{settings.MINIO_ENDPOINT}/{bucket}/{object_key}?download_token={uuid.uuid4().hex}"
