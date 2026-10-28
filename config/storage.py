"""Django storage that uses Vercel Blob in production and local files locally."""

import os
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class VercelBlobStorage(Storage):
    """File storage for public catalogue media or private user uploads."""

    def __init__(self, access="public"):
        if access not in {"public", "private"}:
            raise ValueError("Vercel Blob access must be 'public' or 'private'.")
        self.access = access

    @property
    def token(self):
        variable = f"BLOB_{self.access.upper()}_READ_WRITE_TOKEN"
        return os.environ.get(variable, "").strip()

    @property
    def local_storage(self):
        return FileSystemStorage(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL,
        )

    @staticmethod
    def _is_remote_name(name):
        return isinstance(name, str) and name.startswith(("https://", "http://"))

    def _require_token(self):
        if not self.token:
            raise ImproperlyConfigured(
                "BLOB_READ_WRITE_TOKEN is required to use Vercel Blob storage."
            )

    def _with_blob_client(self, operation, *args, **kwargs):
        """Run a synchronous Blob SDK operation with this store's credentials."""
        from vercel.api import session
        from vercel.blob import BlobCredentials, CredentialKind
        from vercel.blob._internal.options import SyncBlobServiceOptions
        from vercel.blob import sync as blob

        token = self.token
        token_body = token.removeprefix("vercel_blob_rw_")
        store_id, separator, secret = token_body.partition("_")
        if not separator or not store_id or not secret:
            raise ImproperlyConfigured("The configured Vercel Blob token is invalid.")
        options = SyncBlobServiceOptions(
            credentials_factory=lambda: BlobCredentials(
                token=token,
                store_id=store_id,
                kind=CredentialKind.READ_WRITE,
            )
        )
        with session(service_options=[options]):
            return getattr(blob, operation)(*args, **kwargs)

    def _save(self, name, content):
        if not self.token:
            return self.local_storage.save(name, content)

        content_type = getattr(content, "content_type", None)
        data = b"".join(content.chunks())
        blob = self._with_blob_client(
            "put_blob",
            name,
            data,
            access=self.access,
            content_type=content_type,
            add_random_suffix=True,
        )
        return blob.url

    def _open(self, name, mode="rb"):
        if not self._is_remote_name(name):
            return self.local_storage.open(name, mode)
        if mode not in {"rb", "r"}:
            raise ValueError("Vercel Blob files can only be opened for reading.")

        self._require_token()
        blob = self._with_blob_client("get_blob", name, access=self.access)
        return ContentFile(blob.body, name=os.path.basename(urlparse(name).path))

    def delete(self, name):
        if not self._is_remote_name(name):
            return self.local_storage.delete(name)

        self._require_token()
        self._with_blob_client("delete_blob", name)

    def exists(self, name):
        if not self._is_remote_name(name):
            if self.token:
                # New remote names are unique; Vercel adds a suffix when saved.
                return False
            return self.local_storage.exists(name)

        self._require_token()
        from vercel.blob.errors import BlobNotFoundError

        try:
            self._with_blob_client("head_blob", name)
        except BlobNotFoundError:
            return False
        return True

    def url(self, name):
        if self._is_remote_name(name):
            return name
        if self.token:
            raise ValueError("Remote Vercel Blob URLs are returned when the file is saved.")
        return self.local_storage.url(name)
