# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import supply_retrieve_params
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
from ..types.supply_list_response import SupplyListResponse
from ..types.supply_retrieve_response import SupplyRetrieveResponse

__all__ = ["SupplyResource", "AsyncSupplyResource"]


class SupplyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SupplyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SupplyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SupplyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return SupplyResourceWithStreamingResponse(self)

    def retrieve(
        self,
        symbol: str,
        *,
        country_code: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        get_feature_contributions: bool | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SupplyRetrieveResponse:
        """
        Returns historical and forecasted supply data for a given commodity and country.
        Country codes follow the UN/LOCODE standard:
        https://unece.org/trade/cefact/unlocode-code-list-country-and-territory

        Args:
          symbol: Asset symbol

          country_code: Country code (UN/LOCODE). If blank, return global data.

          end_date: End of date range for supply forecasts (YYYY-MM-DD)

          get_feature_contributions: Return feature contributions for requested forecasts.

          model: Supply model to use for forecasting.

          start_date: Start of date range for supply forecasts (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return self._get(
            f"/v1/supply/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "country_code": country_code,
                        "end_date": end_date,
                        "get_feature_contributions": get_feature_contributions,
                        "model": model,
                        "start_date": start_date,
                    },
                    supply_retrieve_params.SupplyRetrieveParams,
                ),
            ),
            cast_to=SupplyRetrieveResponse,
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
    ) -> SupplyListResponse:
        """Returns a list of all commodities that have supply models available.

        Country
        codes follow the UN/LOCODE standard:
        https://unece.org/trade/cefact/unlocode-code-list-country-and-territory
        """
        return self._get(
            "/v1/supply",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SupplyListResponse,
        )


class AsyncSupplyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSupplyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSupplyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSupplyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncSupplyResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        symbol: str,
        *,
        country_code: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        get_feature_contributions: bool | NotGiven = NOT_GIVEN,
        model: str | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SupplyRetrieveResponse:
        """
        Returns historical and forecasted supply data for a given commodity and country.
        Country codes follow the UN/LOCODE standard:
        https://unece.org/trade/cefact/unlocode-code-list-country-and-territory

        Args:
          symbol: Asset symbol

          country_code: Country code (UN/LOCODE). If blank, return global data.

          end_date: End of date range for supply forecasts (YYYY-MM-DD)

          get_feature_contributions: Return feature contributions for requested forecasts.

          model: Supply model to use for forecasting.

          start_date: Start of date range for supply forecasts (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not symbol:
            raise ValueError(f"Expected a non-empty value for `symbol` but received {symbol!r}")
        return await self._get(
            f"/v1/supply/{symbol}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "country_code": country_code,
                        "end_date": end_date,
                        "get_feature_contributions": get_feature_contributions,
                        "model": model,
                        "start_date": start_date,
                    },
                    supply_retrieve_params.SupplyRetrieveParams,
                ),
            ),
            cast_to=SupplyRetrieveResponse,
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
    ) -> SupplyListResponse:
        """Returns a list of all commodities that have supply models available.

        Country
        codes follow the UN/LOCODE standard:
        https://unece.org/trade/cefact/unlocode-code-list-country-and-territory
        """
        return await self._get(
            "/v1/supply",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SupplyListResponse,
        )


class SupplyResourceWithRawResponse:
    def __init__(self, supply: SupplyResource) -> None:
        self._supply = supply

        self.retrieve = to_raw_response_wrapper(
            supply.retrieve,
        )
        self.list = to_raw_response_wrapper(
            supply.list,
        )


class AsyncSupplyResourceWithRawResponse:
    def __init__(self, supply: AsyncSupplyResource) -> None:
        self._supply = supply

        self.retrieve = async_to_raw_response_wrapper(
            supply.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            supply.list,
        )


class SupplyResourceWithStreamingResponse:
    def __init__(self, supply: SupplyResource) -> None:
        self._supply = supply

        self.retrieve = to_streamed_response_wrapper(
            supply.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            supply.list,
        )


class AsyncSupplyResourceWithStreamingResponse:
    def __init__(self, supply: AsyncSupplyResource) -> None:
        self._supply = supply

        self.retrieve = async_to_streamed_response_wrapper(
            supply.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            supply.list,
        )
