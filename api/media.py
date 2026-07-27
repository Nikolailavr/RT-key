"""
Media API.
"""

from __future__ import annotations

from .client import RTKeyApiClient


class RTKeyMediaApi(RTKeyApiClient):
    """Media API."""

    async def download_image(
        self,
        url: str,
    ) -> bytes:
        """Download image."""

        return await self.get_bytes(url)