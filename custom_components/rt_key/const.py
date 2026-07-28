"""Constants for the Ростелеком Ключ integration."""
import logging
from typing import Final

DOMAIN: Final = "rt_key"
LOGGER = logging.getLogger(__package__)

# Configuration
CONF_PHONE: Final = "phone"
CONF_PASSWORD: Final = "password"
CONF_TOKEN: Final = "token"
CONF_REFRESH_TOKEN: Final = "refresh_token"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_DEVICE_ID: Final = "device_id"

# Defaults
DEFAULT_NAME: Final = "Ростелеком Ключ"
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds

# API Base URLs
API_HOUSEHOLD_BASE_URL: Final = "https://household.key.rt.ru/api/v2/app"
API_KEYAPIS_BASE_URL: Final = "https://keyapis.key.rt.ru"
API_VC_BASE_URL: Final = "https://vc.key.rt.ru/api/v1"

API_AUTH_LOGIN_BY_PASSWORD: Final = f"{API_KEYAPIS_BASE_URL}/identity/api/v1/authorization/login_by_password"
API_AUTH_SEND_SMS: Final = f"{API_KEYAPIS_BASE_URL}/identity/api/v1/authorization/send_code"
API_AUTH_VERIFY_SMS: Final = f"{API_KEYAPIS_BASE_URL}/identity/api/v1/authorization/login"
API_AUTH_REFRESH: Final = f"{API_KEYAPIS_BASE_URL}/identity/api/v1/authorization/refresh"

API_DEVICES_URL: Final = f"{API_HOUSEHOLD_BASE_URL}/devices"
API_USERS_CURRENT_URL: Final = "https://household.key.rt.ru/api/v3/app/users/current"
API_INTERCOMS_URL: Final = f"{API_HOUSEHOLD_BASE_URL}/devices/intercom"
API_BARRIERS_URL: Final = f"{API_HOUSEHOLD_BASE_URL}/devices/barrier"
API_CAMERAS_URL: Final = f"{API_HOUSEHOLD_BASE_URL}/devices/cameras"
API_VC_CAMERAS_URL: Final = f"{API_VC_BASE_URL}/cameras"
API_GUEST_CODES_URL: Final = f"{API_HOUSEHOLD_BASE_URL}/devices/guest-codes"
API_TAGS_LIST_URL: Final = f"{API_KEYAPIS_BASE_URL}/tag/api/v1/tag/list"
API_CAMERA_VIDEO_DATA_LIST_URL: Final = f"{API_KEYAPIS_BASE_URL}/vc/api/v1/camera_video_data/list?paging.limit=100&paging.offset=0"

# Platforms
PLATFORMS: Final = [
    "lock",
    "camera",
    "sensor",
    "binary_sensor",
    "button",
]

# Device Types
TYPE_INTERCOM: Final = "intercom"
TYPE_BARRIER: Final = "barrier"
TYPE_GATE: Final = "gate"
TYPE_CAMERA: Final = "camera"

# Services
SERVICE_CREATE_GUEST_CODE: Final = "create_guest_code"
SERVICE_OPEN_DOOR: Final = "open_door"
SERVICE_OPEN_BARRIER: Final = "open_barrier"

ATTR_DURATION_HOURS: Final = "duration_hours"
ATTR_MAX_USES: Final = "max_uses"
ATTR_DESCRIPTION: Final = "description"
ATTR_CODE: Final = "code"
