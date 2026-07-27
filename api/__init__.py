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


class RTKeyApi(
    RTKeyAuthApi,
    RTKeyCameraApi,
    RTKeyIntercomApi,
    RTKeyMediaApi,
):
    """Main RTKey API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        auth: RTKeySession,
    ) -> None:

        super().__init__(
            session=session,
            auth=auth,
        )