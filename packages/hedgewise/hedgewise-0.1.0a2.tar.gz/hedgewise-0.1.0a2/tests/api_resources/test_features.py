# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types import (
    TransformedFeature,
    FeatureListResponse,
    FeatureRetrieveHistoricalResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFeatures:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Hedgewise) -> None:
        feature = client.features.list()
        assert_matches_type(FeatureListResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Hedgewise) -> None:
        feature = client.features.list(
            symbol="ZC",
        )
        assert_matches_type(FeatureListResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Hedgewise) -> None:
        response = client.features.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = response.parse()
        assert_matches_type(FeatureListResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Hedgewise) -> None:
        with client.features.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = response.parse()
            assert_matches_type(FeatureListResponse, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_weighted_index(self, client: Hedgewise) -> None:
        feature = client.features.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_weighted_index_with_all_params(self, client: Hedgewise) -> None:
        feature = client.features.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
            end_date="2025-03-18",
            start_date="2025-02-18",
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_weighted_index(self, client: Hedgewise) -> None:
        response = client.features.with_raw_response.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = response.parse()
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_weighted_index(self, client: Hedgewise) -> None:
        with client.features.with_streaming_response.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = response.parse()
            assert_matches_type(TransformedFeature, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_historical(self, client: Hedgewise) -> None:
        feature = client.features.retrieve_historical(
            feature_code="vietnam_t2mean",
        )
        assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_historical_with_all_params(self, client: Hedgewise) -> None:
        feature = client.features.retrieve_historical(
            feature_code="vietnam_t2mean",
            add_strength_for_commodity="KC",
            agg="mean",
            end_date="2025-03-18",
            freq="weekly",
            start_date="2025-02-18",
        )
        assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_historical(self, client: Hedgewise) -> None:
        response = client.features.with_raw_response.retrieve_historical(
            feature_code="vietnam_t2mean",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = response.parse()
        assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_historical(self, client: Hedgewise) -> None:
        with client.features.with_streaming_response.retrieve_historical(
            feature_code="vietnam_t2mean",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = response.parse()
            assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_historical(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `feature_code` but received ''"):
            client.features.with_raw_response.retrieve_historical(
                feature_code="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_transform_historical(self, client: Hedgewise) -> None:
        feature = client.features.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_transform_historical_with_all_params(self, client: Hedgewise) -> None:
        feature = client.features.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
            end_date="2025-03-18",
            number_of_years=5,
            start_date="2025-02-18",
            window=3,
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_transform_historical(self, client: Hedgewise) -> None:
        response = client.features.with_raw_response.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = response.parse()
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_transform_historical(self, client: Hedgewise) -> None:
        with client.features.with_streaming_response.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = response.parse()
            assert_matches_type(TransformedFeature, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_transform_historical(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `feature_code` but received ''"):
            client.features.with_raw_response.transform_historical(
                feature_code="",
                transform="xyavg",
            )


class TestAsyncFeatures:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.list()
        assert_matches_type(FeatureListResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.list(
            symbol="ZC",
        )
        assert_matches_type(FeatureListResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.features.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = await response.parse()
        assert_matches_type(FeatureListResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHedgewise) -> None:
        async with async_client.features.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = await response.parse()
            assert_matches_type(FeatureListResponse, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_weighted_index(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_weighted_index_with_all_params(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
            end_date="2025-03-18",
            start_date="2025-02-18",
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_weighted_index(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.features.with_raw_response.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = await response.parse()
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_weighted_index(self, async_client: AsyncHedgewise) -> None:
        async with async_client.features.with_streaming_response.get_weighted_index(
            feature_codes=["string"],
            index_label="user_defined_index",
            weights=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = await response.parse()
            assert_matches_type(TransformedFeature, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_historical(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.retrieve_historical(
            feature_code="vietnam_t2mean",
        )
        assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_historical_with_all_params(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.retrieve_historical(
            feature_code="vietnam_t2mean",
            add_strength_for_commodity="KC",
            agg="mean",
            end_date="2025-03-18",
            freq="weekly",
            start_date="2025-02-18",
        )
        assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_historical(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.features.with_raw_response.retrieve_historical(
            feature_code="vietnam_t2mean",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = await response.parse()
        assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_historical(self, async_client: AsyncHedgewise) -> None:
        async with async_client.features.with_streaming_response.retrieve_historical(
            feature_code="vietnam_t2mean",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = await response.parse()
            assert_matches_type(FeatureRetrieveHistoricalResponse, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_historical(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `feature_code` but received ''"):
            await async_client.features.with_raw_response.retrieve_historical(
                feature_code="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_transform_historical(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_transform_historical_with_all_params(self, async_client: AsyncHedgewise) -> None:
        feature = await async_client.features.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
            end_date="2025-03-18",
            number_of_years=5,
            start_date="2025-02-18",
            window=3,
        )
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_transform_historical(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.features.with_raw_response.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature = await response.parse()
        assert_matches_type(TransformedFeature, feature, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_transform_historical(self, async_client: AsyncHedgewise) -> None:
        async with async_client.features.with_streaming_response.transform_historical(
            feature_code="vietnam_t2mean",
            transform="xyavg",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature = await response.parse()
            assert_matches_type(TransformedFeature, feature, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_transform_historical(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `feature_code` but received ''"):
            await async_client.features.with_raw_response.transform_historical(
                feature_code="",
                transform="xyavg",
            )
