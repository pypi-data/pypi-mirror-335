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
from ....types.assets.futures import forecast_get_params, forecast_get_long_term_params
from ....types.assets.futures.forecast_get_response import ForecastGetResponse
from ....types.assets.futures.forecast_get_long_term_response import ForecastGetLongTermResponse

__all__ = ["ForecastsResource", "AsyncForecastsResource"]


class ForecastsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ForecastsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ForecastsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ForecastsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return ForecastsResourceWithStreamingResponse(self)

    def get(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        estimate_uncertainty: bool | NotGiven = NOT_GIVEN,
        get_market_drivers: bool | NotGiven = NOT_GIVEN,
        get_moving_averages: bool | NotGiven = NOT_GIVEN,
        interpolate: bool | NotGiven = NOT_GIVEN,
        price_collar_sigma: float | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForecastGetResponse:
        """Returns a list of all forecasts made for a given future symbol.

        Forecasts are
        made at various horizons, and can be interpolated to daily values. Forecasted
        prices, estimated lower and upper bounds, and market drivers are available for
        each forecast.

        Args:
          symbol: Future symbol

          end_date: End of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          estimate_uncertainty: Estimate prediction uncertainty based on recent historical accuracy.

          get_market_drivers: Return market drivers for each forecast.

          get_moving_averages: Return moving averages for each forecast.

          interpolate: Interpolate between forecast horizons and return daily forecast.

          price_collar_sigma: Apply an empirical price collar to the forecasts. This regulates the forecast
              when it suggests implausibly large price changes. A smaller number results in a
              more aggressive collar. Must be a positive number.

          start_date: Start of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return self._get(
            f"/v1/assets/futures/forecasts/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "estimate_uncertainty": estimate_uncertainty,
                        "get_market_drivers": get_market_drivers,
                        "get_moving_averages": get_moving_averages,
                        "interpolate": interpolate,
                        "price_collar_sigma": price_collar_sigma,
                        "start_date": start_date,
                    },
                    forecast_get_params.ForecastGetParams,
                ),
            ),
            cast_to=ForecastGetResponse,
        )

    def get_long_term(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        horizon: Optional[int] | NotGiven = NOT_GIVEN,
        rollover_type: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForecastGetLongTermResponse:
        """
        Returns a list of booleans indicating whether the price of the given future is
        expected to increase over the next 12 months.

        Args:
          symbol: Future symbol

          end_date: End of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          horizon: Number of months to forecast. _Default value_ : Shortest available term for
              requested symbol.

          rollover_type: Which rollover method to use. _Default value_ : hist_vol

          start_date: Start of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return self._get(
            f"/v1/assets/futures/forecasts/{symbol}/long_term_forecast",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "horizon": horizon,
                        "rollover_type": rollover_type,
                        "start_date": start_date,
                    },
                    forecast_get_long_term_params.ForecastGetLongTermParams,
                ),
            ),
            cast_to=ForecastGetLongTermResponse,
        )


class AsyncForecastsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncForecastsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncForecastsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncForecastsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncForecastsResourceWithStreamingResponse(self)

    async def get(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        estimate_uncertainty: bool | NotGiven = NOT_GIVEN,
        get_market_drivers: bool | NotGiven = NOT_GIVEN,
        get_moving_averages: bool | NotGiven = NOT_GIVEN,
        interpolate: bool | NotGiven = NOT_GIVEN,
        price_collar_sigma: float | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForecastGetResponse:
        """Returns a list of all forecasts made for a given future symbol.

        Forecasts are
        made at various horizons, and can be interpolated to daily values. Forecasted
        prices, estimated lower and upper bounds, and market drivers are available for
        each forecast.

        Args:
          symbol: Future symbol

          end_date: End of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          estimate_uncertainty: Estimate prediction uncertainty based on recent historical accuracy.

          get_market_drivers: Return market drivers for each forecast.

          get_moving_averages: Return moving averages for each forecast.

          interpolate: Interpolate between forecast horizons and return daily forecast.

          price_collar_sigma: Apply an empirical price collar to the forecasts. This regulates the forecast
              when it suggests implausibly large price changes. A smaller number results in a
              more aggressive collar. Must be a positive number.

          start_date: Start of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return await self._get(
            f"/v1/assets/futures/forecasts/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "estimate_uncertainty": estimate_uncertainty,
                        "get_market_drivers": get_market_drivers,
                        "get_moving_averages": get_moving_averages,
                        "interpolate": interpolate,
                        "price_collar_sigma": price_collar_sigma,
                        "start_date": start_date,
                    },
                    forecast_get_params.ForecastGetParams,
                ),
            ),
            cast_to=ForecastGetResponse,
        )

    async def get_long_term(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        horizon: Optional[int] | NotGiven = NOT_GIVEN,
        rollover_type: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ForecastGetLongTermResponse:
        """
        Returns a list of booleans indicating whether the price of the given future is
        expected to increase over the next 12 months.

        Args:
          symbol: Future symbol

          end_date: End of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          horizon: Number of months to forecast. _Default value_ : Shortest available term for
              requested symbol.

          rollover_type: Which rollover method to use. _Default value_ : hist_vol

          start_date: Start of forecast window (YYYY-MM-DD). The returned object will contain every
              forecast made between start*date and end_date. \\__Default value* : most recent
              date with forecasts

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return await self._get(
            f"/v1/assets/futures/forecasts/{symbol}/long_term_forecast",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "horizon": horizon,
                        "rollover_type": rollover_type,
                        "start_date": start_date,
                    },
                    forecast_get_long_term_params.ForecastGetLongTermParams,
                ),
            ),
            cast_to=ForecastGetLongTermResponse,
        )


class ForecastsResourceWithRawResponse:
    def __init__(self, forecasts: ForecastsResource) -> None:
        self._forecasts = forecasts

        self.get = to_raw_response_wrapper(
            forecasts.get,
        )
        self.get_long_term = to_raw_response_wrapper(
            forecasts.get_long_term,
        )


class AsyncForecastsResourceWithRawResponse:
    def __init__(self, forecasts: AsyncForecastsResource) -> None:
        self._forecasts = forecasts

        self.get = async_to_raw_response_wrapper(
            forecasts.get,
        )
        self.get_long_term = async_to_raw_response_wrapper(
            forecasts.get_long_term,
        )


class ForecastsResourceWithStreamingResponse:
    def __init__(self, forecasts: ForecastsResource) -> None:
        self._forecasts = forecasts

        self.get = to_streamed_response_wrapper(
            forecasts.get,
        )
        self.get_long_term = to_streamed_response_wrapper(
            forecasts.get_long_term,
        )


class AsyncForecastsResourceWithStreamingResponse:
    def __init__(self, forecasts: AsyncForecastsResource) -> None:
        self._forecasts = forecasts

        self.get = async_to_streamed_response_wrapper(
            forecasts.get,
        )
        self.get_long_term = async_to_streamed_response_wrapper(
            forecasts.get_long_term,
        )
