from typing import BinaryIO, Generator

from google.cloud.storage import Blob, Bucket  # type: ignore
from google.cloud.storage.client import Client  # type: ignore

from gcutils.exceptions import BlobNotFound

# TODO: Should I throw errors in JSON format so they are easier to analyze downstream?

# TODO: How is the default retry in the google client?


class GSutils:
    __CLIENTS: dict[str, Client] = {}
    __BUCKETS: dict[str, Bucket] = {}

    def __init__(self, project_id: str) -> None:
        if not project_id in self.__CLIENTS:
            self.__CLIENTS[project_id] = Client(project=project_id)
        self._client: Client = self.__CLIENTS[project_id]

    def list_buckets(self, prefix: str | None) -> Generator[Bucket, None, None]:
        for bucket in self._client.list_buckets(prefix=prefix):
            yield bucket

    def get_bucket(self, bucket_or_name: Bucket | str) -> Bucket:
        if isinstance(bucket_or_name, Bucket):
            return bucket_or_name
        if bucket_or_name in self.__BUCKETS:
            return self.__BUCKETS[bucket_or_name]
        return self._client.get_bucket(bucket_or_name=bucket_or_name)

    def list_blobs(
        self, bucket_or_name: Bucket | str, prefix: str | None, limit: int | None
    ) -> Generator[Blob, None, None]:
        bucket = self.get_bucket(bucket_or_name=bucket_or_name)
        for blob in bucket.list_blobs(prefix=prefix, max_results=limit):
            yield blob

    def get_blob(self, bucket_or_name: Bucket | str, blob_name: str) -> Blob:
        bucket = self.get_bucket(bucket_or_name=bucket_or_name)
        blob: Blob | None = bucket.get_blob(blob_name=blob_name)
        if not blob:
            raise BlobNotFound(
                f"Could not find Blob with name: {blob_name} in bucket: {bucket.name}"
            )
        return blob

    def blob_download_as_bytes(
        self, blob: Blob, start: int | None, end: int | None
    ) -> bytes:
        b: bytes = blob.download_as_bytes(start=start, end=end)
        return b

    def blob_download_as_text(
        self, blob: Blob, start: int | None, end: int | None
    ) -> str:
        text: str = blob.download_as_text(start=start, end=end)
        return text

    def blob_download_to_file(
        self, file_obj: BinaryIO, blob: Blob, start: int | None, end: int | None
    ) -> None:
        blob.download_to_file(file_obj=file_obj, start=start, end=end)
