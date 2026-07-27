"""Exceptions for RTKey."""


class RTKeyError(Exception):
    """Base exception."""


class RTKeyApiError(RTKeyError):
    """API error."""


class RTKeyAuthError(RTKeyApiError):
    """Authentication failed."""


class RTKeyConnectionError(RTKeyApiError):
    """Network error."""


class RTKeyInvalidResponse(RTKeyApiError):
    """Invalid response."""