# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from .futures.futures import (
    FuturesResource,
    AsyncFuturesResource,
    FuturesResourceWithRawResponse,
    AsyncFuturesResourceWithRawResponse,
    FuturesResourceWithStreamingResponse,
    AsyncFuturesResourceWithStreamingResponse,
)
from ...types.asset_list_response import AssetListResponse

__all__ = ["AssetsResource", "AsyncAssetsResource"]


class AssetsResource(SyncAPIResource):
    @cached_property
    def futures(self) -> FuturesResource:
        return FuturesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AssetsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetListResponse:
        """Returns a list of all available asset categories, such as futures.

        Prices,
        forecasts, and indicators are available for each.
        """
        return self._get(
            "/v1/assets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetListResponse,
        )


class AsyncAssetsResource(AsyncAPIResource):
    @cached_property
    def futures(self) -> AsyncFuturesResource:
        return AsyncFuturesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncAssetsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetListResponse:
        """Returns a list of all available asset categories, such as futures.

        Prices,
        forecasts, and indicators are available for each.
        """
        return await self._get(
            "/v1/assets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetListResponse,
        )


class AssetsResourceWithRawResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_raw_response_wrapper(
            assets.list,
        )

    @cached_property
    def futures(self) -> FuturesResourceWithRawResponse:
        return FuturesResourceWithRawResponse(self._assets.futures)


class AsyncAssetsResourceWithRawResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_raw_response_wrapper(
            assets.list,
        )

    @cached_property
    def futures(self) -> AsyncFuturesResourceWithRawResponse:
        return AsyncFuturesResourceWithRawResponse(self._assets.futures)


class AssetsResourceWithStreamingResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_streamed_response_wrapper(
            assets.list,
        )

    @cached_property
    def futures(self) -> FuturesResourceWithStreamingResponse:
        return FuturesResourceWithStreamingResponse(self._assets.futures)


class AsyncAssetsResourceWithStreamingResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_streamed_response_wrapper(
            assets.list,
        )

    @cached_property
    def futures(self) -> AsyncFuturesResourceWithStreamingResponse:
        return AsyncFuturesResourceWithStreamingResponse(self._assets.futures)
