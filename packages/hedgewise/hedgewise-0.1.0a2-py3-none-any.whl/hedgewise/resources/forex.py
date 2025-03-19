# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import forex_retrieve_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.forex_list_response import ForexListResponse
from ..types.forex_retrieve_response import ForexRetrieveResponse

__all__ = ["ForexResource", "AsyncForexResource"]


class ForexResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ForexResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ForexResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ForexResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return ForexResourceWithStreamingResponse(self)

    def retrieve(
        self,
        code: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        foreign_per_usd: bool | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForexRetrieveResponse:
        """
        Returns forex price history for a given currency code.

        Args:
          code: Forex code

          end_date: End of forex data window (YYYY-MM-DD)

          foreign_per_usd: Return prices as foreign currency per USD. If false, prices will be returned as
              USD per foreign currency.

          start_date: Start of forex data window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return self._get(
            f"/v1/forex/{code}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "foreign_per_usd": foreign_per_usd,
                        "start_date": start_date,
                    },
                    forex_retrieve_params.ForexRetrieveParams,
                ),
            ),
            cast_to=ForexRetrieveResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForexListResponse:
        """Get most recent forex prices for all currencies"""
        return self._get(
            "/v1/forex",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForexListResponse,
        )


class AsyncForexResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncForexResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncForexResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncForexResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncForexResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        code: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        foreign_per_usd: bool | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForexRetrieveResponse:
        """
        Returns forex price history for a given currency code.

        Args:
          code: Forex code

          end_date: End of forex data window (YYYY-MM-DD)

          foreign_per_usd: Return prices as foreign currency per USD. If false, prices will be returned as
              USD per foreign currency.

          start_date: Start of forex data window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return await self._get(
            f"/v1/forex/{code}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "foreign_per_usd": foreign_per_usd,
                        "start_date": start_date,
                    },
                    forex_retrieve_params.ForexRetrieveParams,
                ),
            ),
            cast_to=ForexRetrieveResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForexListResponse:
        """Get most recent forex prices for all currencies"""
        return await self._get(
            "/v1/forex",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ForexListResponse,
        )


class ForexResourceWithRawResponse:
    def __init__(self, forex: ForexResource) -> None:
        self._forex = forex

        self.retrieve = to_raw_response_wrapper(
            forex.retrieve,
        )
        self.list = to_raw_response_wrapper(
            forex.list,
        )


class AsyncForexResourceWithRawResponse:
    def __init__(self, forex: AsyncForexResource) -> None:
        self._forex = forex

        self.retrieve = async_to_raw_response_wrapper(
            forex.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            forex.list,
        )


class ForexResourceWithStreamingResponse:
    def __init__(self, forex: ForexResource) -> None:
        self._forex = forex

        self.retrieve = to_streamed_response_wrapper(
            forex.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            forex.list,
        )


class AsyncForexResourceWithStreamingResponse:
    def __init__(self, forex: AsyncForexResource) -> None:
        self._forex = forex

        self.retrieve = async_to_streamed_response_wrapper(
            forex.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            forex.list,
        )
