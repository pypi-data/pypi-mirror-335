# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.models import performance_retrieve_params
from ...types.models.performance_list_response import PerformanceListResponse
from ...types.models.performance_retrieve_response import PerformanceRetrieveResponse

__all__ = ["PerformanceResource", "AsyncPerformanceResource"]


class PerformanceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PerformanceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PerformanceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PerformanceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return PerformanceResourceWithStreamingResponse(self)

    def retrieve(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        horizon: Optional[int] | NotGiven = NOT_GIVEN,
        metric: Optional[str] | NotGiven = NOT_GIVEN,
        sigma: float | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        threshold_on_actual: Optional[float] | NotGiven = NOT_GIVEN,
        threshold_on_forecast: Optional[float] | NotGiven = NOT_GIVEN,
        use_run_date: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PerformanceRetrieveResponse:
        """
        The metrics values are not provided as-is, but the relevant data and recommended
        aggregation method for each metric is returned.

        Args:
          symbol: Future symbol

          end_date: End of the performance assessment window (YYYY-MM-DD)

          horizon: the horizon (number of business days in the future) of the model of interest.
              Default, returns for all horizons

          metric: the requested metric as described in the metadata. Default: hitrate

          sigma: Number of standard deviations to calculate for ACE. Unused for other metrics.

          start_date: Start of the performance assessment window (YYYY-MM-DD)

          threshold_on_actual: Allows to assess directional performance filtered on days where the % realized
              price change is greater than threshold. Default: no filter. Valid only for
              hitrate style metrics. Eg. enter 0.02 for 2%

          threshold_on_forecast: Allows to assess directional performance filtered on days where the % expected
              change of the forecast is greater than threshold. Default: no filter. Valid only
              for hitrate style metrics. Eg. enter 0.02 for 2%

          use_run_date: Use the run date of the forecast to filter the performance assessment window. If
              false, use the target date. Setting this to false makes the result deterministic
              from day to day.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return self._get(
            f"/v1/models/performance/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "horizon": horizon,
                        "metric": metric,
                        "sigma": sigma,
                        "start_date": start_date,
                        "threshold_on_actual": threshold_on_actual,
                        "threshold_on_forecast": threshold_on_forecast,
                        "use_run_date": use_run_date,
                    },
                    performance_retrieve_params.PerformanceRetrieveParams,
                ),
            ),
            cast_to=PerformanceRetrieveResponse,
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
    ) -> PerformanceListResponse:
        """
        Returns the list of success data that can be requested to assess our forecasting
        models performance
        """
        return self._get(
            "/v1/models/performance",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PerformanceListResponse,
        )


class AsyncPerformanceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPerformanceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPerformanceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPerformanceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncPerformanceResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        symbol: str,
        *,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        horizon: Optional[int] | NotGiven = NOT_GIVEN,
        metric: Optional[str] | NotGiven = NOT_GIVEN,
        sigma: float | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        threshold_on_actual: Optional[float] | NotGiven = NOT_GIVEN,
        threshold_on_forecast: Optional[float] | NotGiven = NOT_GIVEN,
        use_run_date: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PerformanceRetrieveResponse:
        """
        The metrics values are not provided as-is, but the relevant data and recommended
        aggregation method for each metric is returned.

        Args:
          symbol: Future symbol

          end_date: End of the performance assessment window (YYYY-MM-DD)

          horizon: the horizon (number of business days in the future) of the model of interest.
              Default, returns for all horizons

          metric: the requested metric as described in the metadata. Default: hitrate

          sigma: Number of standard deviations to calculate for ACE. Unused for other metrics.

          start_date: Start of the performance assessment window (YYYY-MM-DD)

          threshold_on_actual: Allows to assess directional performance filtered on days where the % realized
              price change is greater than threshold. Default: no filter. Valid only for
              hitrate style metrics. Eg. enter 0.02 for 2%

          threshold_on_forecast: Allows to assess directional performance filtered on days where the % expected
              change of the forecast is greater than threshold. Default: no filter. Valid only
              for hitrate style metrics. Eg. enter 0.02 for 2%

          use_run_date: Use the run date of the forecast to filter the performance assessment window. If
              false, use the target date. Setting this to false makes the result deterministic
              from day to day.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return await self._get(
            f"/v1/models/performance/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "horizon": horizon,
                        "metric": metric,
                        "sigma": sigma,
                        "start_date": start_date,
                        "threshold_on_actual": threshold_on_actual,
                        "threshold_on_forecast": threshold_on_forecast,
                        "use_run_date": use_run_date,
                    },
                    performance_retrieve_params.PerformanceRetrieveParams,
                ),
            ),
            cast_to=PerformanceRetrieveResponse,
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
    ) -> PerformanceListResponse:
        """
        Returns the list of success data that can be requested to assess our forecasting
        models performance
        """
        return await self._get(
            "/v1/models/performance",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PerformanceListResponse,
        )


class PerformanceResourceWithRawResponse:
    def __init__(self, performance: PerformanceResource) -> None:
        self._performance = performance

        self.retrieve = to_raw_response_wrapper(
            performance.retrieve,
        )
        self.list = to_raw_response_wrapper(
            performance.list,
        )


class AsyncPerformanceResourceWithRawResponse:
    def __init__(self, performance: AsyncPerformanceResource) -> None:
        self._performance = performance

        self.retrieve = async_to_raw_response_wrapper(
            performance.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            performance.list,
        )


class PerformanceResourceWithStreamingResponse:
    def __init__(self, performance: PerformanceResource) -> None:
        self._performance = performance

        self.retrieve = to_streamed_response_wrapper(
            performance.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            performance.list,
        )


class AsyncPerformanceResourceWithStreamingResponse:
    def __init__(self, performance: AsyncPerformanceResource) -> None:
        self._performance = performance

        self.retrieve = async_to_streamed_response_wrapper(
            performance.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            performance.list,
        )
