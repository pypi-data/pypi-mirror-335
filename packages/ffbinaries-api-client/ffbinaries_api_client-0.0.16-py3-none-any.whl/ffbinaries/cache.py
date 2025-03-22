"""Simple Cache Module."""

import time
from typing import Any

from ffbinaries.exceptions import (
    ExpiredCacheDataError,
    InvalidArgumentError,
    NoCacheDataError,
)


class SimpleCache:
    """Very Simple Cache Class."""

    def __init__(self, cache_age: float) -> None:
        if not isinstance(cache_age, float) or cache_age <= 0:
            msg = 'cache_age value needs to be int or float and greater than 0'
            raise InvalidArgumentError(msg)

        self._cache_age = cache_age
        self._cache: dict[str, tuple[int, dict[str, Any]]] = {}

    def get_cached_items(self) -> dict:
        return self._cache.copy()

    def add(self, url: str, data: dict[str, Any]) -> None:
        self._cache[url] = (int(time.time()), data)

    def get(self, url: str) -> dict[str, Any]:
        try:
            if int(time.time()) - self._cache[url][0] < self._cache_age:
                return self._cache[url][1]
        except KeyError as err:
            raise NoCacheDataError from err

        del self._cache[url]
        raise ExpiredCacheDataError
