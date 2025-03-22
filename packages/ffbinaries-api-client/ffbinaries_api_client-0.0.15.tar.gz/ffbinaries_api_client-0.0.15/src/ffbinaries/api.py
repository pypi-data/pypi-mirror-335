"""ffbinaries API Client Module."""

import logging
import posixpath
from multiprocessing import Lock as ProcLock
from threading import Lock as ThreadLock
from typing import TYPE_CHECKING, Any, Final, Literal

from cache import SimpleCache
from enums import APIVersionType, ComponentType, HTTPMethodType, PlatformCodeType
from exceptions import (
    ExpiredCacheDataError,
    FFBinariesAPIClientError,
    NoCacheDataError,
)
from requests import Response, Session
from utils import is_float

if TYPE_CHECKING:
    from collections.abc import KeysView

PROC_LOCK: Final[ProcLock] = ProcLock()
THREAD_LOCK: Final[ThreadLock] = ThreadLock()


class FFBinariesV1APIClient:
    """ffbinaries API Client Class."""

    BASE_API_URL: Final[str] = 'https://ffbinaries.com/api'
    API_VERSION: Literal[APIVersionType.V1] = APIVersionType.V1

    ENDPOINT_VERSIONS: Final[str] = 'versions'
    ENDPOINT_VERSION: Final[str] = 'version'
    ENDPOINT_LATEST: Final[str] = f'{ENDPOINT_VERSION}/latest'
    ENDPOINT_EXACT_VERSION: Final[str] = f'{ENDPOINT_VERSION}/{{}}'

    DEFAULT_CACHE_AGE: Final[int] = 300
    DEFAULT_REQUEST_TIMEOUT: Final[int] = 60

    def __init__(
        self,
        use_caching: bool = False,
        cache_age: float = DEFAULT_CACHE_AGE,
        request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._use_caching = use_caching
        self._cache = SimpleCache(cache_age)
        self._request_timeout = request_timeout

        self._session = Session()

    def _request(
        self,
        url: str,
        method: HTTPMethodType = HTTPMethodType.GET,
        stream: bool = False,
        jsonify: bool = False,
    ) -> Response | dict[str, Any]:
        """General Request Method."""

        def _get_data_() -> Response | dict[str, Any]:
            return self.__make_request(
                url=url, method=method, stream=stream, jsonify=jsonify
            )

        # Cache only JSON-data which should be directly returned to the caller.
        if all((jsonify, self._use_caching, self._valid_for_caching(url=url))):
            with THREAD_LOCK, PROC_LOCK:
                try:
                    return self._cache.get(url=url)
                except (ExpiredCacheDataError, NoCacheDataError):
                    data: dict[str, Any] = _get_data_()
                    self._cache.add(url=url, data=data)
                    return data
        return _get_data_()

    def __make_request(
        self, url: str, method: HTTPMethodType, stream: bool, jsonify: bool
    ) -> Response | dict[str, Any]:
        self._log.debug('%s %s ', method, url)
        response = self._session.request(
            method=method, url=url, stream=stream, timeout=self._request_timeout
        )
        return response.json() if jsonify else response

    def _valid_for_caching(self, url: str) -> bool:
        return self.BASE_API_URL in url

    def get_latest_metadata(self) -> dict[str, Any]:
        url = posixpath.join(self.BASE_API_URL, self.API_VERSION, self.ENDPOINT_LATEST)
        return self._request(url=url, jsonify=True)

    def get_available_versions_metadata(self) -> dict[str, Any]:
        url = posixpath.join(
            self.BASE_API_URL, self.API_VERSION, self.ENDPOINT_VERSIONS
        )
        return self._request(url=url, jsonify=True)

    def get_exact_version_metadata(self, version: str) -> dict[str, Any]:
        url = posixpath.join(
            self.BASE_API_URL,
            self.API_VERSION,
            self.ENDPOINT_EXACT_VERSION.format(version),
        )
        return self._request(url=url, jsonify=True)

    def get_latest_version(self) -> str:
        try:
            return self.get_latest_metadata()['version']
        except KeyError as err:
            msg = f'Failed to get latest published version: {err}'
            raise FFBinariesAPIClientError(msg) from err

    def get_available_versions(self) -> list[str]:
        metadata = self.get_available_versions_metadata()
        try:
            versions_view: KeysView[str] = metadata['versions']
        except KeyError as err:
            msg = f'Failed to get available versions: {err}'
            raise FFBinariesAPIClientError(msg) from err

        # Check if version can be converted to float but use original
        # string version for compatibility with API response.
        # If got regular non-float string e.g. 'latest', skip it.
        return [v for v in versions_view if is_float(value=v)]

    def download_latest_version(
        self, component: ComponentType, platform: PlatformCodeType, stream: bool = False
    ) -> Response:
        try:
            url: str = self.get_latest_metadata()['bin'][platform][component]
        except KeyError as err:
            msg = f'Failed to download latest version: {err}'
            raise FFBinariesAPIClientError(msg) from err
        return self._request(url=url, stream=stream)

    def download_exact_version(
        self,
        component: ComponentType,
        version: str,
        platform: PlatformCodeType,
        stream: bool = False,
    ) -> Response:
        metadata = self.get_exact_version_metadata(version=version)
        try:
            url: str = metadata['bin'][platform][component]
        except KeyError as err:
            msg = f'Failed to download exact version: {err}'
            raise FFBinariesAPIClientError(msg) from err
        return self._request(url=url, stream=stream)

    def show_cache(self) -> dict[str, Any]:
        return self._cache.get_cached_items()
