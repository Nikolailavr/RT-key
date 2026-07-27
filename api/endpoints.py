"""
RTKey API endpoints.
"""

from __future__ import annotations

AUTH_BASE = "https://keyapis.key.rt.ru"

API_BASE = "https://household.key.rt.ru"

MEDIA_BASE = "https://media-vdk4.camera.rt.ru"

LIVE_BASE = "https://live-vdk4.camera.rt.ru"


#
# Authorization
#

SEND_CODE = (
    f"{AUTH_BASE}/identity/api/v1/authorization/send_code"
)

LOGIN = (
    f"{AUTH_BASE}/identity/api/v1/authorization/login"
)


#
# User
#

CURRENT_USER = (
    f"{API_BASE}/api/v3/app/users/current"
)


#
# Devices
#

INTERCOMS = (
    f"{API_BASE}/api/v2/app/devices/intercom"
)

OPEN_DOOR = (
    f"{API_BASE}/api/v2/app/devices/{{device_id}}/open"
)


#
# Cameras
#

CAMERA_LIST = (
    f"{API_BASE}/vc/api/v1/camera_video_data/list"
)

STREAM = (
    f"{LIVE_BASE}/stream/{{camera_id}}/{{stream_token}}.mp4"
)