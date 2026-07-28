"""Exceptions for Rostelecom Key API."""

class RostelecomKeyException(Exception):
    """Base exception for Rostelecom Key."""

class RostelecomKeyAuthError(RostelecomKeyException):
    """Authentication failure exception."""

class RostelecomKeyApiError(RostelecomKeyException):
    """General API communication exception."""

class RostelecomKeyNetworkError(RostelecomKeyApiError):
    """Network connection error."""
