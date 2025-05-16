from app.ports.storage import IStoragePort
from botocore.client import Config
from app.config import Settings
import boto3
import io


class S3StorageAdapter(IStoragePort):
    def __init__(self):
        self.__client = boto3.client(
            "s3",
            endpoint_url=Settings.S3_ENDPOINT,
            aws_access_key_id=Settings.S3_ACCESS_KEY,
            aws_secret_access_key=Settings.S3_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def upload_jpeg(self, buf: io.BytesIO, bucket: str, key: str) -> None:
        self.__client.upload_fileobj(
            buf,
            bucket,
            key,
            ExtraArgs={"ContentType": "image/jpeg"},
        )

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

    def get_object(self, bucket: str, key: str) -> dict:
        return self.__client.get_object(Bucket=bucket, Key=key)

    def ensure_bucket(self, bucket: str) -> None:
        if self.__client.bucket_exists(bucket):
            return

        raise RuntimeError(f"Необходимо определить бакет {bucket}!")
