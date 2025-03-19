# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types.assets.futures import (
    ForecastGetResponse,
    ForecastGetLongTermResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestForecasts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Hedgewise) -> None:
        forecast = client.assets.futures.forecasts.get(
            symbol="ZC",
        )
        assert_matches_type(ForecastGetResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_with_all_params(self, client: Hedgewise) -> None:
        forecast = client.assets.futures.forecasts.get(
            symbol="ZC",
            end_date="2025-03-17",
            estimate_uncertainty=True,
            get_market_drivers=True,
            get_moving_averages=True,
            interpolate=True,
            price_collar_sigma=0,
            start_date="2025-03-17",
        )
        assert_matches_type(ForecastGetResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Hedgewise) -> None:
        response = client.assets.futures.forecasts.with_raw_response.get(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forecast = response.parse()
        assert_matches_type(ForecastGetResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Hedgewise) -> None:
        with client.assets.futures.forecasts.with_streaming_response.get(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forecast = response.parse()
            assert_matches_type(ForecastGetResponse, forecast, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            client.assets.futures.forecasts.with_raw_response.get(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_long_term(self, client: Hedgewise) -> None:
        forecast = client.assets.futures.forecasts.get_long_term(
            symbol="ZC",
        )
        assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_long_term_with_all_params(self, client: Hedgewise) -> None:
        forecast = client.assets.futures.forecasts.get_long_term(
            symbol="ZC",
            end_date="2025-03-18",
            horizon=12,
            rollover_type="hist_vol",
            start_date="2025-02-18",
        )
        assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_long_term(self, client: Hedgewise) -> None:
        response = client.assets.futures.forecasts.with_raw_response.get_long_term(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forecast = response.parse()
        assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_long_term(self, client: Hedgewise) -> None:
        with client.assets.futures.forecasts.with_streaming_response.get_long_term(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forecast = response.parse()
            assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_long_term(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            client.assets.futures.forecasts.with_raw_response.get_long_term(
                symbol="",
            )


class TestAsyncForecasts:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncHedgewise) -> None:
        forecast = await async_client.assets.futures.forecasts.get(
            symbol="ZC",
        )
        assert_matches_type(ForecastGetResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncHedgewise) -> None:
        forecast = await async_client.assets.futures.forecasts.get(
            symbol="ZC",
            end_date="2025-03-17",
            estimate_uncertainty=True,
            get_market_drivers=True,
            get_moving_averages=True,
            interpolate=True,
            price_collar_sigma=0,
            start_date="2025-03-17",
        )
        assert_matches_type(ForecastGetResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.assets.futures.forecasts.with_raw_response.get(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forecast = await response.parse()
        assert_matches_type(ForecastGetResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncHedgewise) -> None:
        async with async_client.assets.futures.forecasts.with_streaming_response.get(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forecast = await response.parse()
            assert_matches_type(ForecastGetResponse, forecast, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            await async_client.assets.futures.forecasts.with_raw_response.get(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_long_term(self, async_client: AsyncHedgewise) -> None:
        forecast = await async_client.assets.futures.forecasts.get_long_term(
            symbol="ZC",
        )
        assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_long_term_with_all_params(self, async_client: AsyncHedgewise) -> None:
        forecast = await async_client.assets.futures.forecasts.get_long_term(
            symbol="ZC",
            end_date="2025-03-18",
            horizon=12,
            rollover_type="hist_vol",
            start_date="2025-02-18",
        )
        assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_long_term(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.assets.futures.forecasts.with_raw_response.get_long_term(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forecast = await response.parse()
        assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_long_term(self, async_client: AsyncHedgewise) -> None:
        async with async_client.assets.futures.forecasts.with_streaming_response.get_long_term(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forecast = await response.parse()
            assert_matches_type(ForecastGetLongTermResponse, forecast, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_long_term(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            await async_client.assets.futures.forecasts.with_raw_response.get_long_term(
                symbol="",
            )
