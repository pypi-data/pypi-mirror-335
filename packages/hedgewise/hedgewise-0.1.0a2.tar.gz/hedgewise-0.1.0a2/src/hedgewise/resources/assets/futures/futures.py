# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .forecasts import (
    ForecastsResource,
    AsyncForecastsResource,
    ForecastsResourceWithRawResponse,
    AsyncForecastsResourceWithRawResponse,
    ForecastsResourceWithStreamingResponse,
    AsyncForecastsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from .indicators import (
    IndicatorsResource,
    AsyncIndicatorsResource,
    IndicatorsResourceWithRawResponse,
    AsyncIndicatorsResourceWithRawResponse,
    IndicatorsResourceWithStreamingResponse,
    AsyncIndicatorsResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.assets import future_get_trading_calendar_params, future_get_historical_prices_params
from ....types.assets.future_list_response import FutureListResponse
from ....types.assets.future_get_trading_calendar_response import FutureGetTradingCalendarResponse
from ....types.assets.future_get_historical_prices_response import FutureGetHistoricalPricesResponse

__all__ = ["FuturesResource", "AsyncFuturesResource"]


class FuturesResource(SyncAPIResource):
    @cached_property
    def forecasts(self) -> ForecastsResource:
        return ForecastsResource(self._client)

    @cached_property
    def indicators(self) -> IndicatorsResource:
        return IndicatorsResource(self._client)

    @cached_property
    def with_raw_response(self) -> FuturesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return FuturesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FuturesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return FuturesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FutureListResponse:
        """Returns a list of all available future symbols that Hedgewise tracks."""
        return self._get(
            "/v1/assets/futures",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FutureListResponse,
        )

    def get_historical_prices(
        self,
        symbol: str,
        *,
        active_contracts_only: bool | NotGiven = NOT_GIVEN,
        back_adjust: bool | NotGiven = NOT_GIVEN,
        contract: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        rollover_method: str | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FutureGetHistoricalPricesResponse:
        """Returns historical price data for a given future symbol.

        Prices are available
        for all actively traded contracts on each day.

        Args:
          symbol: Future symbol

          active_contracts_only: Return price data for currently active contracts only. Set to false to also
              retrieve price data from expired contracts.

          back_adjust: Back-adjust prices to account for calendar spread at contract rollover dates.
              The method used is described here:
              https://www.sierrachart.com/index.php?page=doc/ContinuousFuturesContractCharts.html#ContinuousFuturesContractDateRuleRolloverBackAdjusted

          contract: Contract year and month. _Default value_ : All available contracts

          end_date: End of prices window (YYYY-MM-DD). The returned object will contain the entire
              price history for every contract that traded between `start_date` and
              `end_date`. Ignored if `contract` is specified. _Default value_ : most recent
              date with prices

          rollover_method: The rollover date is the most recent date for which a given contract was trading
              as the front month. This parameter specifies the method used to determine the
              rollover date for contracts. Must be one of "hist_vol", "max_vol",
              "first_notice", or "last_trade" (or left blank for no rollover calculation).
              "first_notice" not available for all commodities, and defaults to "last_trade".

          start_date: Start of prices window (YYYY-MM-DD). The returned object will contain the entire
              price history for every contract that traded between `start_date` and
              `end_date`. Ignored if `contract` is specified. _Default value_ : most recent
              date with prices

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return self._get(
            f"/v1/assets/futures/prices/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "active_contracts_only": active_contracts_only,
                        "back_adjust": back_adjust,
                        "contract": contract,
                        "end_date": end_date,
                        "rollover_method": rollover_method,
                        "start_date": start_date,
                    },
                    future_get_historical_prices_params.FutureGetHistoricalPricesParams,
                ),
            ),
            cast_to=FutureGetHistoricalPricesResponse,
        )

    def get_trading_calendar(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FutureGetTradingCalendarResponse:
        """
        Returns a list of all trading days for a given future symbol, based on the
        exchange where its contracts are traded. Prices, forecasts, and indicators are
        available for each of these days.

        Args:
          symbol: Future symbol

          end_date: End of trading calendar window (YYYY-MM-DD)

          start_date: Start of trading calendar window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return self._get(
            f"/v1/assets/futures/calendars/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "start_date": start_date,
                    },
                    future_get_trading_calendar_params.FutureGetTradingCalendarParams,
                ),
            ),
            cast_to=FutureGetTradingCalendarResponse,
        )


class AsyncFuturesResource(AsyncAPIResource):
    @cached_property
    def forecasts(self) -> AsyncForecastsResource:
        return AsyncForecastsResource(self._client)

    @cached_property
    def indicators(self) -> AsyncIndicatorsResource:
        return AsyncIndicatorsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncFuturesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFuturesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFuturesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncFuturesResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FutureListResponse:
        """Returns a list of all available future symbols that Hedgewise tracks."""
        return await self._get(
            "/v1/assets/futures",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FutureListResponse,
        )

    async def get_historical_prices(
        self,
        symbol: str,
        *,
        active_contracts_only: bool | NotGiven = NOT_GIVEN,
        back_adjust: bool | NotGiven = NOT_GIVEN,
        contract: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        rollover_method: str | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FutureGetHistoricalPricesResponse:
        """Returns historical price data for a given future symbol.

        Prices are available
        for all actively traded contracts on each day.

        Args:
          symbol: Future symbol

          active_contracts_only: Return price data for currently active contracts only. Set to false to also
              retrieve price data from expired contracts.

          back_adjust: Back-adjust prices to account for calendar spread at contract rollover dates.
              The method used is described here:
              https://www.sierrachart.com/index.php?page=doc/ContinuousFuturesContractCharts.html#ContinuousFuturesContractDateRuleRolloverBackAdjusted

          contract: Contract year and month. _Default value_ : All available contracts

          end_date: End of prices window (YYYY-MM-DD). The returned object will contain the entire
              price history for every contract that traded between `start_date` and
              `end_date`. Ignored if `contract` is specified. _Default value_ : most recent
              date with prices

          rollover_method: The rollover date is the most recent date for which a given contract was trading
              as the front month. This parameter specifies the method used to determine the
              rollover date for contracts. Must be one of "hist_vol", "max_vol",
              "first_notice", or "last_trade" (or left blank for no rollover calculation).
              "first_notice" not available for all commodities, and defaults to "last_trade".

          start_date: Start of prices window (YYYY-MM-DD). The returned object will contain the entire
              price history for every contract that traded between `start_date` and
              `end_date`. Ignored if `contract` is specified. _Default value_ : most recent
              date with prices

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return await self._get(
            f"/v1/assets/futures/prices/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "active_contracts_only": active_contracts_only,
                        "back_adjust": back_adjust,
                        "contract": contract,
                        "end_date": end_date,
                        "rollover_method": rollover_method,
                        "start_date": start_date,
                    },
                    future_get_historical_prices_params.FutureGetHistoricalPricesParams,
                ),
            ),
            cast_to=FutureGetHistoricalPricesResponse,
        )

    async def get_trading_calendar(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FutureGetTradingCalendarResponse:
        """
        Returns a list of all trading days for a given future symbol, based on the
        exchange where its contracts are traded. Prices, forecasts, and indicators are
        available for each of these days.

        Args:
          symbol: Future symbol

          end_date: End of trading calendar window (YYYY-MM-DD)

          start_date: Start of trading calendar window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return await self._get(
            f"/v1/assets/futures/calendars/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "start_date": start_date,
                    },
                    future_get_trading_calendar_params.FutureGetTradingCalendarParams,
                ),
            ),
            cast_to=FutureGetTradingCalendarResponse,
        )


class FuturesResourceWithRawResponse:
    def __init__(self, futures: FuturesResource) -> None:
        self._futures = futures

        self.list = to_raw_response_wrapper(
            futures.list,
        )
        self.get_historical_prices = to_raw_response_wrapper(
            futures.get_historical_prices,
        )
        self.get_trading_calendar = to_raw_response_wrapper(
            futures.get_trading_calendar,
        )

    @cached_property
    def forecasts(self) -> ForecastsResourceWithRawResponse:
        return ForecastsResourceWithRawResponse(self._futures.forecasts)

    @cached_property
    def indicators(self) -> IndicatorsResourceWithRawResponse:
        return IndicatorsResourceWithRawResponse(self._futures.indicators)


class AsyncFuturesResourceWithRawResponse:
    def __init__(self, futures: AsyncFuturesResource) -> None:
        self._futures = futures

        self.list = async_to_raw_response_wrapper(
            futures.list,
        )
        self.get_historical_prices = async_to_raw_response_wrapper(
            futures.get_historical_prices,
        )
        self.get_trading_calendar = async_to_raw_response_wrapper(
            futures.get_trading_calendar,
        )

    @cached_property
    def forecasts(self) -> AsyncForecastsResourceWithRawResponse:
        return AsyncForecastsResourceWithRawResponse(self._futures.forecasts)

    @cached_property
    def indicators(self) -> AsyncIndicatorsResourceWithRawResponse:
        return AsyncIndicatorsResourceWithRawResponse(self._futures.indicators)


class FuturesResourceWithStreamingResponse:
    def __init__(self, futures: FuturesResource) -> None:
        self._futures = futures

        self.list = to_streamed_response_wrapper(
            futures.list,
        )
        self.get_historical_prices = to_streamed_response_wrapper(
            futures.get_historical_prices,
        )
        self.get_trading_calendar = to_streamed_response_wrapper(
            futures.get_trading_calendar,
        )

    @cached_property
    def forecasts(self) -> ForecastsResourceWithStreamingResponse:
        return ForecastsResourceWithStreamingResponse(self._futures.forecasts)

    @cached_property
    def indicators(self) -> IndicatorsResourceWithStreamingResponse:
        return IndicatorsResourceWithStreamingResponse(self._futures.indicators)


class AsyncFuturesResourceWithStreamingResponse:
    def __init__(self, futures: AsyncFuturesResource) -> None:
        self._futures = futures

        self.list = async_to_streamed_response_wrapper(
            futures.list,
        )
        self.get_historical_prices = async_to_streamed_response_wrapper(
            futures.get_historical_prices,
        )
        self.get_trading_calendar = async_to_streamed_response_wrapper(
            futures.get_trading_calendar,
        )

    @cached_property
    def forecasts(self) -> AsyncForecastsResourceWithStreamingResponse:
        return AsyncForecastsResourceWithStreamingResponse(self._futures.forecasts)

    @cached_property
    def indicators(self) -> AsyncIndicatorsResourceWithStreamingResponse:
        return AsyncIndicatorsResourceWithStreamingResponse(self._futures.indicators)
