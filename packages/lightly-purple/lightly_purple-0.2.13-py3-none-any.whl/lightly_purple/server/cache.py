"""This module contains the FastAPI cache configuration for static files."""

from datetime import datetime, timedelta, timezone

from fastapi import Response
from fastapi.staticfiles import StaticFiles

from .routes.api.status import HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE


class StaticFilesCache(StaticFiles):
    """StaticFiles class with cache headers."""

    days_to_expire = 365

    def __init__(
        self,
        *args,
        cachecontrol=f"private, max-age={days_to_expire * 24 * 60 * 60}",
        **kwargs,
    ):
        """Initialize the StaticFilesCache class."""
        self.cachecontrol = cachecontrol
        super().__init__(*args, **kwargs)

    def file_response(self, *args, **kwargs) -> Response:
        """Override the file_response method to add cache headers."""
        allowed_extensions = (
            # Images
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".bmp",
            ".gif",
            ".tiff",
            # Movies
            ".mov",
            ".mp4",
            ".avi",
        )

        if not args[0].lower().endswith(allowed_extensions):
            return Response(
                status_code=HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE
            )  # Unsupported Media Type
        resp: Response = super().file_response(*args, **kwargs)
        resp.headers.setdefault("Cache-Control", self.cachecontrol)

        # Calculate expiration date
        expire_date = datetime.now(timezone.utc) + timedelta(
            days=self.days_to_expire
        )
        resp.headers.setdefault(
            "Expires", expire_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        )

        return resp
