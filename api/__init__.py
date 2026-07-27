"""
RTKey API.
"""

from __future__ import annotations

import aiohttp

from .auth import RTKeyAuthApi
from .camera import RTKeyCameraApi
from .intercom import RTKeyIntercomApi
from .media import RTKeyMediaApi
from .session import RTKeySession

__all__ = [
    "RTKeyApi",
    "RTKeySession",
]


class RTKeyApi:
    """Main RTKey API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        auth: RTKeySession,
    ) -> None:
        """Initialize API."""

        self.session = auth

        self.auth = RTKeyAuthApi(
            session=session,
            auth=auth,
        )

        self.camera = RTKeyCameraApi(
            session=session,
            auth=auth,
        )

        self.intercom = RTKeyIntercomApi(
            session=session,
            auth=auth,
        )

        self.media = RTKeyMediaApi(
            session=session,
            auth=auth,
        )