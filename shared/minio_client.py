import os
import boto3
from botocore.client import Config

# Default MinIO settings (can be overridden by environment variables)
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_REGION = os.getenv('MINIO_REGION', 'us-east-1')


def get_minio_client():
    """
    Returns a boto3 S3 client configured for MinIO.
    """
    return boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name=MINIO_REGION,
        config=Config(signature_version='s3v4'),
    )

