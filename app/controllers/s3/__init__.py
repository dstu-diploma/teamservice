from botocore.client import Config
from app.config import Settings
from functools import lru_cache
from datetime import timedelta
from typing import Protocol
import boto3
import io


class IS3Controller(Protocol):
    def upload_file(
        self, buf: io.BytesIO, bucket: str, key: str, content_type: str
    ) -> None: ...
    def delete_object(self, bucket: str, key: str) -> None: ...
    def object_exists(self, bucket: str, key: str) -> bool: ...
    def ensure_bucket(self, bucket: str) -> None: ...
    def generate_presigned_url(
        self, bucket: str, key: str, expires_in: timedelta
    ) -> str: ...
    def get_object(self, bucket: str, key: str): ...


class S3Controller(IS3Controller):
    def __init__(self):
        self.__client = boto3.client(
            "s3",
            endpoint_url=Settings.S3_ENDPOINT,
            aws_access_key_id=Settings.S3_ACCESS_KEY,
            aws_secret_access_key=Settings.S3_SECRET_KEY,
            config=Config(
                signature_version="s3v4", s3={"addressing_style": "path"}
            ),
            region_name="us-east-1",
        )

    def get_object(self, bucket: str, key: str):
        return self.__client.get_object(Bucket=bucket, Key=key)

    def upload_file(
        self, buf: io.BytesIO, bucket: str, key: str, content_type: str
    ) -> None:
        self.__client.upload_fileobj(
            buf,
            bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )

    def delete_object(self, bucket: str, key: str) -> None:
        self.__client.delete_object(Bucket=bucket, Key=key)

    def object_exists(self, bucket: str, key: str) -> bool:
        try:
            self.__client.head_object(Bucket=bucket, Key=key)
            return True
        except self.__client.exceptions.ClientError:
            return False

    def ensure_bucket(self, bucket: str) -> None:
        if self.__client.bucket_exists(bucket):
            return

        raise RuntimeError(f"Необходимо определить бакет {bucket}!")

    def generate_presigned_url(
        self, bucket: str, key: str, expires_in: timedelta
    ) -> str:
        return self.__client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=int(expires_in.total_seconds()),
        )


@lru_cache
def get_s3_controller() -> S3Controller:
    return S3Controller()
