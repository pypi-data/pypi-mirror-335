# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional

import httpx

from ..types import (
    feature_list_params,
    feature_get_weighted_index_params,
    feature_retrieve_historical_params,
    feature_transform_historical_params,
)
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
from ..types.transformed_feature import TransformedFeature
from ..types.feature_list_response import FeatureListResponse
from ..types.feature_retrieve_historical_response import FeatureRetrieveHistoricalResponse

__all__ = ["FeaturesResource", "AsyncFeaturesResource"]


class FeaturesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FeaturesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return FeaturesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FeaturesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return FeaturesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        symbol: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FeatureListResponse:
        """
        Returns the list of all available features that Hedgewise tracks or produces.
        Some of these are used to produce our price and commodity production forecasts.

        Args:
          symbol: Future symbol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/features",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"symbol": symbol}, feature_list_params.FeatureListParams),
            ),
            cast_to=FeatureListResponse,
        )

    def get_weighted_index(
        self,
        *,
        feature_codes: List[str],
        index_label: str,
        weights: Iterable[float],
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformedFeature:
        """
        Provides a facility to create an index formed as a weighted basket of the list
        of features provided. The features provided must exist and listed as available
        at the `/v1/features` endpoint.

        Args:
          feature_codes: The list of features to include in the index

          index_label: user defined string used to name the weighted index

          weights: The list of weights to apply on the features selection to create the index

          end_date: End of transformed feature data window (YYYY-MM-DD)

          start_date: Start of transformed feature data window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/features/weighted_index/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "feature_codes": feature_codes,
                        "index_label": index_label,
                        "weights": weights,
                        "end_date": end_date,
                        "start_date": start_date,
                    },
                    feature_get_weighted_index_params.FeatureGetWeightedIndexParams,
                ),
            ),
            cast_to=TransformedFeature,
        )

    def retrieve_historical(
        self,
        feature_code: str,
        *,
        add_strength_for_commodity: Optional[str] | NotGiven = NOT_GIVEN,
        agg: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        freq: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FeatureRetrieveHistoricalResponse:
        """Returns historical values for a given feature code.

        The feature code is a unique
        identifier for a specific feature, such as weather or crop health data. Feature
        codes can be obtained with the `/v1/features` endpoint.

        Args:
          feature_code: Feature code

          add_strength_for_commodity: If a future symbol is provided and a model for that commodity exists, a signed
              strength indicator will be returned in addition to the feature value

          agg: If a `weekly` or `monthly` frequency is requested, this parameter allows to
              control how the returned data is aggregated over each period. `mean` and `last`
              are supported

          end_date: End of feature data window (YYYY-MM-DD)

          freq: By default, time-series are returned using daily time frequency. Request
              resampled data using `weekly` or `monthly` as query parameter

          start_date: Start of feature data window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not feature_code:
            raise ValueError(f"Expected a non-empty value for `feature_code` but received {feature_code!r}")
        return self._get(
            f"/v1/features/historical/{feature_code}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "add_strength_for_commodity": add_strength_for_commodity,
                        "agg": agg,
                        "end_date": end_date,
                        "freq": freq,
                        "start_date": start_date,
                    },
                    feature_retrieve_historical_params.FeatureRetrieveHistoricalParams,
                ),
            ),
            cast_to=FeatureRetrieveHistoricalResponse,
        )

    def transform_historical(
        self,
        feature_code: str,
        *,
        transform: str,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        number_of_years: int | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        window: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformedFeature:
        """
        Provides a facility to apply transformation like computing the average of 5
        years or transpose the features time-series to create a year-on-year
        representation of the time-series of the features Feature codes can be obtained
        with the `/v1/features` endpoint.

        Args:
          feature_code: Feature code

          transform: The type of transform requested. Currently supported are `xyavg`, `rebase`,
              `zscore`, `yoy`

          end_date: End of transformed feature data window (YYYY-MM-DD) - not relevant for yoy

          number_of_years: Number of years to perform the average on. (valid for xyavg and yoy transforms)

          start_date: Start of transformed feature data window (YYYY-MM-DD) - not relevant for yoy

          window: Number of observations used in the transformation window. (valid for xyavg and
              zscore transforms)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not feature_code:
            raise ValueError(f"Expected a non-empty value for `feature_code` but received {feature_code!r}")
        return self._get(
            f"/v1/features/transform/{feature_code}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "transform": transform,
                        "end_date": end_date,
                        "number_of_years": number_of_years,
                        "start_date": start_date,
                        "window": window,
                    },
                    feature_transform_historical_params.FeatureTransformHistoricalParams,
                ),
            ),
            cast_to=TransformedFeature,
        )


class AsyncFeaturesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFeaturesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFeaturesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFeaturesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/descarteslabs/hedgewise-sdk-python#with_streaming_response
        """
        return AsyncFeaturesResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        symbol: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FeatureListResponse:
        """
        Returns the list of all available features that Hedgewise tracks or produces.
        Some of these are used to produce our price and commodity production forecasts.

        Args:
          symbol: Future symbol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/features",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"symbol": symbol}, feature_list_params.FeatureListParams),
            ),
            cast_to=FeatureListResponse,
        )

    async def get_weighted_index(
        self,
        *,
        feature_codes: List[str],
        index_label: str,
        weights: Iterable[float],
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformedFeature:
        """
        Provides a facility to create an index formed as a weighted basket of the list
        of features provided. The features provided must exist and listed as available
        at the `/v1/features` endpoint.

        Args:
          feature_codes: The list of features to include in the index

          index_label: user defined string used to name the weighted index

          weights: The list of weights to apply on the features selection to create the index

          end_date: End of transformed feature data window (YYYY-MM-DD)

          start_date: Start of transformed feature data window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/features/weighted_index/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "feature_codes": feature_codes,
                        "index_label": index_label,
                        "weights": weights,
                        "end_date": end_date,
                        "start_date": start_date,
                    },
                    feature_get_weighted_index_params.FeatureGetWeightedIndexParams,
                ),
            ),
            cast_to=TransformedFeature,
        )

    async def retrieve_historical(
        self,
        feature_code: str,
        *,
        add_strength_for_commodity: Optional[str] | NotGiven = NOT_GIVEN,
        agg: Optional[str] | NotGiven = NOT_GIVEN,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        freq: Optional[str] | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FeatureRetrieveHistoricalResponse:
        """Returns historical values for a given feature code.

        The feature code is a unique
        identifier for a specific feature, such as weather or crop health data. Feature
        codes can be obtained with the `/v1/features` endpoint.

        Args:
          feature_code: Feature code

          add_strength_for_commodity: If a future symbol is provided and a model for that commodity exists, a signed
              strength indicator will be returned in addition to the feature value

          agg: If a `weekly` or `monthly` frequency is requested, this parameter allows to
              control how the returned data is aggregated over each period. `mean` and `last`
              are supported

          end_date: End of feature data window (YYYY-MM-DD)

          freq: By default, time-series are returned using daily time frequency. Request
              resampled data using `weekly` or `monthly` as query parameter

          start_date: Start of feature data window (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not feature_code:
            raise ValueError(f"Expected a non-empty value for `feature_code` but received {feature_code!r}")
        return await self._get(
            f"/v1/features/historical/{feature_code}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "add_strength_for_commodity": add_strength_for_commodity,
                        "agg": agg,
                        "end_date": end_date,
                        "freq": freq,
                        "start_date": start_date,
                    },
                    feature_retrieve_historical_params.FeatureRetrieveHistoricalParams,
                ),
            ),
            cast_to=FeatureRetrieveHistoricalResponse,
        )

    async def transform_historical(
        self,
        feature_code: str,
        *,
        transform: str,
        end_date: Optional[str] | NotGiven = NOT_GIVEN,
        number_of_years: int | NotGiven = NOT_GIVEN,
        start_date: Optional[str] | NotGiven = NOT_GIVEN,
        window: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformedFeature:
        """
        Provides a facility to apply transformation like computing the average of 5
        years or transpose the features time-series to create a year-on-year
        representation of the time-series of the features Feature codes can be obtained
        with the `/v1/features` endpoint.

        Args:
          feature_code: Feature code

          transform: The type of transform requested. Currently supported are `xyavg`, `rebase`,
              `zscore`, `yoy`

          end_date: End of transformed feature data window (YYYY-MM-DD) - not relevant for yoy

          number_of_years: Number of years to perform the average on. (valid for xyavg and yoy transforms)

          start_date: Start of transformed feature data window (YYYY-MM-DD) - not relevant for yoy

          window: Number of observations used in the transformation window. (valid for xyavg and
              zscore transforms)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not feature_code:
            raise ValueError(f"Expected a non-empty value for `feature_code` but received {feature_code!r}")
        return await self._get(
            f"/v1/features/transform/{feature_code}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "transform": transform,
                        "end_date": end_date,
                        "number_of_years": number_of_years,
                        "start_date": start_date,
                        "window": window,
                    },
                    feature_transform_historical_params.FeatureTransformHistoricalParams,
                ),
            ),
            cast_to=TransformedFeature,
        )


class FeaturesResourceWithRawResponse:
    def __init__(self, features: FeaturesResource) -> None:
        self._features = features

        self.list = to_raw_response_wrapper(
            features.list,
        )
        self.get_weighted_index = to_raw_response_wrapper(
            features.get_weighted_index,
        )
        self.retrieve_historical = to_raw_response_wrapper(
            features.retrieve_historical,
        )
        self.transform_historical = to_raw_response_wrapper(
            features.transform_historical,
        )


class AsyncFeaturesResourceWithRawResponse:
    def __init__(self, features: AsyncFeaturesResource) -> None:
        self._features = features

        self.list = async_to_raw_response_wrapper(
            features.list,
        )
        self.get_weighted_index = async_to_raw_response_wrapper(
            features.get_weighted_index,
        )
        self.retrieve_historical = async_to_raw_response_wrapper(
            features.retrieve_historical,
        )
        self.transform_historical = async_to_raw_response_wrapper(
            features.transform_historical,
        )


class FeaturesResourceWithStreamingResponse:
    def __init__(self, features: FeaturesResource) -> None:
        self._features = features

        self.list = to_streamed_response_wrapper(
            features.list,
        )
        self.get_weighted_index = to_streamed_response_wrapper(
            features.get_weighted_index,
        )
        self.retrieve_historical = to_streamed_response_wrapper(
            features.retrieve_historical,
        )
        self.transform_historical = to_streamed_response_wrapper(
            features.transform_historical,
        )


class AsyncFeaturesResourceWithStreamingResponse:
    def __init__(self, features: AsyncFeaturesResource) -> None:
        self._features = features

        self.list = async_to_streamed_response_wrapper(
            features.list,
        )
        self.get_weighted_index = async_to_streamed_response_wrapper(
            features.get_weighted_index,
        )
        self.retrieve_historical = async_to_streamed_response_wrapper(
            features.retrieve_historical,
        )
        self.transform_historical = async_to_streamed_response_wrapper(
            features.transform_historical,
        )
