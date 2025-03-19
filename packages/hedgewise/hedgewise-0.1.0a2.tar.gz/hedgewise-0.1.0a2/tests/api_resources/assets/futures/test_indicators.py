# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types.assets.futures import IndicatorListResponse, IndicatorGetHedgeResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIndicators:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Hedgewise) -> None:
        indicator = client.assets.futures.indicators.list()
        assert_matches_type(IndicatorListResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Hedgewise) -> None:
        response = client.assets.futures.indicators.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        indicator = response.parse()
        assert_matches_type(IndicatorListResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Hedgewise) -> None:
        with client.assets.futures.indicators.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            indicator = response.parse()
            assert_matches_type(IndicatorListResponse, indicator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_hedge(self, client: Hedgewise) -> None:
        indicator = client.assets.futures.indicators.get_hedge(
            symbol="ZC",
        )
        assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_hedge_with_all_params(self, client: Hedgewise) -> None:
        indicator = client.assets.futures.indicators.get_hedge(
            symbol="ZC",
            contract="2025H",
            end_date="2025-03-17",
            hedge_horizon=5,
            lookback_days=30,
            start_date="2025-02-18",
        )
        assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_hedge(self, client: Hedgewise) -> None:
        response = client.assets.futures.indicators.with_raw_response.get_hedge(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        indicator = response.parse()
        assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_hedge(self, client: Hedgewise) -> None:
        with client.assets.futures.indicators.with_streaming_response.get_hedge(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            indicator = response.parse()
            assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_hedge(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            client.assets.futures.indicators.with_raw_response.get_hedge(
                symbol="",
            )


class TestAsyncIndicators:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncHedgewise) -> None:
        indicator = await async_client.assets.futures.indicators.list()
        assert_matches_type(IndicatorListResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.assets.futures.indicators.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        indicator = await response.parse()
        assert_matches_type(IndicatorListResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHedgewise) -> None:
        async with async_client.assets.futures.indicators.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            indicator = await response.parse()
            assert_matches_type(IndicatorListResponse, indicator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_hedge(self, async_client: AsyncHedgewise) -> None:
        indicator = await async_client.assets.futures.indicators.get_hedge(
            symbol="ZC",
        )
        assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_hedge_with_all_params(self, async_client: AsyncHedgewise) -> None:
        indicator = await async_client.assets.futures.indicators.get_hedge(
            symbol="ZC",
            contract="2025H",
            end_date="2025-03-17",
            hedge_horizon=5,
            lookback_days=30,
            start_date="2025-02-18",
        )
        assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_hedge(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.assets.futures.indicators.with_raw_response.get_hedge(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        indicator = await response.parse()
        assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_hedge(self, async_client: AsyncHedgewise) -> None:
        async with async_client.assets.futures.indicators.with_streaming_response.get_hedge(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            indicator = await response.parse()
            assert_matches_type(IndicatorGetHedgeResponse, indicator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_hedge(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            await async_client.assets.futures.indicators.with_raw_response.get_hedge(
                symbol="",
            )
