import hashlib
import os
import io
import boto3
from botocore.config import Config
from app.config import settings


class StorageService:
    def __init__(self):
        self.s3_client = None
        if settings.S3_ENDPOINT_URL and settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION,
                    config=Config(signature_version="s3v4")
                )
                # Ensure bucket exists
                self._ensure_bucket()
            except Exception as e:
                print(f"[StorageService] Warning: Failed to connect to S3/MinIO ({e}). Will use local file fallback.")
                self.s3_client = None

        self.local_storage_dir = os.path.join(os.getcwd(), "storage_data")
        os.makedirs(self.local_storage_dir, exist_ok=True)

    def _ensure_bucket(self):
        if not self.s3_client:
            return
        try:
            self.s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        except Exception:
            try:
                self.s3_client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            except Exception as e:
                print(f"[StorageService] Failed to create S3 bucket {settings.S3_BUCKET_NAME}: {e}")

    @staticmethod
    def compute_sha256(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def generate_upload_url(self, object_key: str, expires_in: int = 3600) -> str:
        if self.s3_client:
            try:
                return self.s3_client.generate_presigned_url(
                    "put_object",
                    Params={
                        "Bucket": settings.S3_BUCKET_NAME,
                        "Key": object_key
                    },
                    ExpiresIn=expires_in
                )
            except Exception as e:
                print(f"[StorageService] Presigned URL error: {e}")
        
        # Fallback local upload URL indicator
        return f"http://localhost:8000/api/v1/images/local-upload/{object_key}"

    def upload_file_bytes(self, object_key: str, file_bytes: bytes, content_type: str = "image/jpeg") -> str:
        if self.s3_client:
            try:
                self.s3_client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=object_key,
                    Body=file_bytes,
                    ContentType=content_type
                )
                return object_key
            except Exception as e:
                print(f"[StorageService] S3 upload error: {e}")

        # Local fallback
        filepath = os.path.join(self.local_storage_dir, object_key)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        return object_key

    def download_file_bytes(self, object_key: str) -> bytes:
        if self.s3_client:
            try:
                response = self.s3_client.get_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=object_key
                )
                return response["Body"].read()
            except Exception as e:
                print(f"[StorageService] S3 download error: {e}")

        filepath = os.path.join(self.local_storage_dir, object_key)
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return f.read()

        raise FileNotFoundError(f"File with key {object_key} not found in S3 or local storage")


storage_service = StorageService()
