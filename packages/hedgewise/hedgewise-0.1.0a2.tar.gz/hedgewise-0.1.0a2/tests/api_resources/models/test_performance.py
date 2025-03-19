# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types.models import PerformanceListResponse, PerformanceRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPerformance:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Hedgewise) -> None:
        performance = client.models.performance.retrieve(
            symbol="ZC",
        )
        assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Hedgewise) -> None:
        performance = client.models.performance.retrieve(
            symbol="ZC",
            end_date="2025-03-18",
            horizon=5,
            metric="hitrate",
            sigma=1,
            start_date="2025-01-01",
            threshold_on_actual=0,
            threshold_on_forecast=0,
            use_run_date=True,
        )
        assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Hedgewise) -> None:
        response = client.models.performance.with_raw_response.retrieve(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        performance = response.parse()
        assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Hedgewise) -> None:
        with client.models.performance.with_streaming_response.retrieve(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            performance = response.parse()
            assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            client.models.performance.with_raw_response.retrieve(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Hedgewise) -> None:
        performance = client.models.performance.list()
        assert_matches_type(PerformanceListResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Hedgewise) -> None:
        response = client.models.performance.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        performance = response.parse()
        assert_matches_type(PerformanceListResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Hedgewise) -> None:
        with client.models.performance.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            performance = response.parse()
            assert_matches_type(PerformanceListResponse, performance, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPerformance:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncHedgewise) -> None:
        performance = await async_client.models.performance.retrieve(
            symbol="ZC",
        )
        assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncHedgewise) -> None:
        performance = await async_client.models.performance.retrieve(
            symbol="ZC",
            end_date="2025-03-18",
            horizon=5,
            metric="hitrate",
            sigma=1,
            start_date="2025-01-01",
            threshold_on_actual=0,
            threshold_on_forecast=0,
            use_run_date=True,
        )
        assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.models.performance.with_raw_response.retrieve(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        performance = await response.parse()
        assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncHedgewise) -> None:
        async with async_client.models.performance.with_streaming_response.retrieve(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            performance = await response.parse()
            assert_matches_type(PerformanceRetrieveResponse, performance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            await async_client.models.performance.with_raw_response.retrieve(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncHedgewise) -> None:
        performance = await async_client.models.performance.list()
        assert_matches_type(PerformanceListResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.models.performance.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        performance = await response.parse()
        assert_matches_type(PerformanceListResponse, performance, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHedgewise) -> None:
        async with async_client.models.performance.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            performance = await response.parse()
            assert_matches_type(PerformanceListResponse, performance, path=["response"])

        assert cast(Any, response.is_closed) is True
