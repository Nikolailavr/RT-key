"""Constants for RTKey."""

from datetime import timedelta

from datetime import timedelta

DOMAIN = "rtkey"

SCAN_INTERVAL = timedelta(seconds=30)

MANUFACTURER = "Ростелеком"

MODEL = "RT Key"

NAME = "Ростелеком Ключ"

CONF_PHONE = "phone"

CONF_TOKEN = "access_token"

CONF_DEVICE_ID = "device_id"

API_URL = "https://household.key.rt.ru"

AUTH_URL = "https://keyapis.key.rt.ru"

CAMERA_URL = "https://media-vdk4.camera.rt.ru"

VC_URL = "https://household.key.rt.ru/vc/api/v1"