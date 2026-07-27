"""
Models for RTKey integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class User:
    """Current user."""

    id: int
    phone: str
    first_name: str | None
    last_name: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "User":
        return cls(
            id=data["id"],
            phone=data["phoneNumber"],
            first_name=data.get("firstName"),
            last_name=data.get("lastName"),
        )


@dataclass(slots=True, frozen=True)
class Intercom:
    """Intercom device."""

    id: int
    name: str
    address: str
    entrance: str | None
    camera_id: str | None
    online: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Intercom":
        return cls(
            id=data["id"],
            name=data.get("name", f"Домофон {data['id']}"),
            address=data.get("address", ""),
            entrance=data.get("entrance"),
            camera_id=data.get("cameraId"),
            online=data.get("online", True),
        )

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Intercom":
        return cls(
            id=data["id"],
            name=data["name"],
            address=data.get("address", ""),
            camera_id=data.get("cameraId"),
            online=data.get("online", True),
        )


@dataclass(slots=True, frozen=True)
class Camera:
    """Camera."""

    id: int              # ID записи в API
    camera_id: str       # UUID камеры
    name: str
    address: str | None
    entrance: str | None
    screenshot_template: str | None
    stream_token: str | None
    cdn_token: str | None
    online: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Camera":
        return cls(
            id=data["id"],
            camera_id=data["cameraId"],
            name=data.get("name", "Камера"),
            address=data.get("address"),
            entrance=data.get("entrance"),
            screenshot_template=data.get(
                "screenshot_precise_url_template"
            ),
            stream_token=data.get("streamToken"),
            cdn_token=data.get("cdnToken"),
            online=data.get("online", True),
        )

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Camera":
        return cls(
            camera_id=data["cameraId"],
            online=data.get("online", True),
            stream_url=data.get("streamUrl"),
            screenshot_url=data.get("screenshotPreciseUrlTemplate"),
        )


@dataclass(slots=True, frozen=True)
class Door:
    """Door."""

    id: int

    intercom_id: int

    name: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Door":
        return cls(
            id=data["id"],
            intercom_id=data["intercomId"],
            name=data.get("name", "Дверь"),
        )


@dataclass(slots=True, frozen=True)
class RTKeyDevice:
    intercom: Intercom
    camera: Camera | None

    @property
    def unique_id(self) -> str:
        return str(self.intercom.id)


    @property
    def name(self) -> str:
        return self.intercom.name


@dataclass(slots=True)
class RTKeyData:
    api: RTKeyApi
    coordinator: RTKeyCoordinator
    session: RTKeySession