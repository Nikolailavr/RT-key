"""
Runtime data for RTKey.
"""

from __future__ import annotations

from dataclasses import dataclass

from .api import RTKeyApi
from .coordinator import RTKeyCoordinator


@dataclass(slots=True)
class RTKeyRuntimeData:
    """Runtime data."""

    api: RTKeyApi
    coordinator: RTKeyCoordinator