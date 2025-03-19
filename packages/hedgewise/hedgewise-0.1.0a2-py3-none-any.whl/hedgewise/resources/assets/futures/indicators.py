# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.assets.futures import indicator_get_hedge_params
from ....types.assets.futures.indicator_list_response import IndicatorListResponse
from ....types.assets.futures.indicator_get_hedge_response import IndicatorGetHedgeResponse

__all__ = ["IndicatorsResource", "AsyncIndicatorsResource"]


class IndicatorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IndicatorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return IndicatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IndicatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return IndicatorsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IndicatorListResponse:
        """
        Returns the list of all available market indicators that Hedgewise tracks or
        produces.
        """
        return self._get(
            "/v1/assets/futures/indicators",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IndicatorListResponse,
        )

    def get_hedge(
        self,
        symbol: str,
        *,
        contract: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        hedge_horizon: Optional[int] | NotGiven = NOT_GIVEN,
        lookback_days: int | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IndicatorGetHedgeResponse:
        """
        Returns a list of values indicating the likelihood that the future price will
        increase, indicating that this is a good time to hedge. The indicator is
        quintiles of the ratio of the forecasted price trajectory (out to a specified
        horizon) to the forecasted ulcer index, where the quintiles are given by
        historical values of this indicator back a specified number of lookback days.

        Args:
          symbol: Future symbol

          contract: Contract year and month. _Default value_ : All available contracts

          end_date: End of indicator window (YYYY-MM-DD). The returned object will contain every
              requested indicator made between start*date and end_date. \\__Default value* :
              most recent date with indicators

          hedge_horizon: Number of trading days in the future to hedge. _Default value_ : Full forecast

          lookback_days: Number of trading days to look back when computing indicator quintiles. _Default
              value_ : 30 days

          start_date: Start of indicator window (YYYY-MM-DD). The returned object will contain every
              requested indicator made between start*date and end_date. \\__Default value* :
              most recent date with indicators

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return self._get(
            f"/v1/assets/futures/indicators/hedge/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "contract": contract,
                        "end_date": end_date,
                        "hedge_horizon": hedge_horizon,
                        "lookback_days": lookback_days,
                        "start_date": start_date,
                    },
                    indicator_get_hedge_params.IndicatorGetHedgeParams,
                ),
            ),
            cast_to=IndicatorGetHedgeResponse,
        )


class AsyncIndicatorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIndicatorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIndicatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIndicatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncIndicatorsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IndicatorListResponse:
        """
        Returns the list of all available market indicators that Hedgewise tracks or
        produces.
        """
        return await self._get(
            "/v1/assets/futures/indicators",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IndicatorListResponse,
        )

    async def get_hedge(
        self,
        symbol: str,
        *,
        contract: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        hedge_horizon: Optional[int] | NotGiven = NOT_GIVEN,
        lookback_days: int | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IndicatorGetHedgeResponse:
        """
        Returns a list of values indicating the likelihood that the future price will
        increase, indicating that this is a good time to hedge. The indicator is
        quintiles of the ratio of the forecasted price trajectory (out to a specified
        horizon) to the forecasted ulcer index, where the quintiles are given by
        historical values of this indicator back a specified number of lookback days.

        Args:
          symbol: Future symbol

          contract: Contract year and month. _Default value_ : All available contracts

          end_date: End of indicator window (YYYY-MM-DD). The returned object will contain every
              requested indicator made between start*date and end_date. \\__Default value* :
              most recent date with indicators

          hedge_horizon: Number of trading days in the future to hedge. _Default value_ : Full forecast

          lookback_days: Number of trading days to look back when computing indicator quintiles. _Default
              value_ : 30 days

          start_date: Start of indicator window (YYYY-MM-DD). The returned object will contain every
              requested indicator made between start*date and end_date. \\__Default value* :
              most recent date with indicators

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return await self._get(
            f"/v1/assets/futures/indicators/hedge/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "contract": contract,
                        "end_date": end_date,
                        "hedge_horizon": hedge_horizon,
                        "lookback_days": lookback_days,
                        "start_date": start_date,
                    },
                    indicator_get_hedge_params.IndicatorGetHedgeParams,
                ),
            ),
            cast_to=IndicatorGetHedgeResponse,
        )


class IndicatorsResourceWithRawResponse:
    def __init__(self, indicators: IndicatorsResource) -> None:
        self._indicators = indicators

        self.list = to_raw_response_wrapper(
            indicators.list,
        )
        self.get_hedge = to_raw_response_wrapper(
            indicators.get_hedge,
        )


class AsyncIndicatorsResourceWithRawResponse:
    def __init__(self, indicators: AsyncIndicatorsResource) -> None:
        self._indicators = indicators

        self.list = async_to_raw_response_wrapper(
            indicators.list,
        )
        self.get_hedge = async_to_raw_response_wrapper(
            indicators.get_hedge,
        )


class IndicatorsResourceWithStreamingResponse:
    def __init__(self, indicators: IndicatorsResource) -> None:
        self._indicators = indicators

        self.list = to_streamed_response_wrapper(
            indicators.list,
        )
        self.get_hedge = to_streamed_response_wrapper(
            indicators.get_hedge,
        )


class AsyncIndicatorsResourceWithStreamingResponse:
    def __init__(self, indicators: AsyncIndicatorsResource) -> None:
        self._indicators = indicators

        self.list = async_to_streamed_response_wrapper(
            indicators.list,
        )
        self.get_hedge = async_to_streamed_response_wrapper(
            indicators.get_hedge,
        )
