"""Exceptions Module."""

__all__ = [
    'CacheError',
    'ExpiredCacheDataError',
    'FFBinariesAPIClientError',
    'InvalidArgumentError',
    'NoCacheDataError',
]


class FFBinariesAPIClientError(Exception):
    """General API Client Error Class."""


class InvalidArgumentError(ValueError):
    """Invalid Argument Exception."""


class CacheError(Exception):
    """Base Cache Error Class."""


class NoCacheDataError(CacheError):
    """Raised when cache doesn't contain queried data."""

    def __str__(self) -> str:
        return 'No cache data'


class ExpiredCacheDataError(CacheError):
    """Expired Cache Data Error Class."""

    def __str__(self) -> str:
        return 'Expired cache data'
