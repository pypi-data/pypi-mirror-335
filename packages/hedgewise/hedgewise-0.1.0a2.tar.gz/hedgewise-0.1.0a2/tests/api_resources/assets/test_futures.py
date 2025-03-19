# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types.assets import (
    FutureListResponse,
    FutureGetTradingCalendarResponse,
    FutureGetHistoricalPricesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFutures:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Hedgewise) -> None:
        future = client.assets.futures.list()
        assert_matches_type(FutureListResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Hedgewise) -> None:
        response = client.assets.futures.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        future = response.parse()
        assert_matches_type(FutureListResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Hedgewise) -> None:
        with client.assets.futures.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            future = response.parse()
            assert_matches_type(FutureListResponse, future, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_historical_prices(self, client: Hedgewise) -> None:
        future = client.assets.futures.get_historical_prices(
            symbol="ZC",
        )
        assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_historical_prices_with_all_params(self, client: Hedgewise) -> None:
        future = client.assets.futures.get_historical_prices(
            symbol="ZC",
            active_contracts_only=True,
            back_adjust=True,
            contract="2025H",
            end_date="2025-03-17",
            rollover_method="hist_vol",
            start_date="2025-03-17",
        )
        assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_historical_prices(self, client: Hedgewise) -> None:
        response = client.assets.futures.with_raw_response.get_historical_prices(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        future = response.parse()
        assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_historical_prices(self, client: Hedgewise) -> None:
        with client.assets.futures.with_streaming_response.get_historical_prices(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            future = response.parse()
            assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_historical_prices(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            client.assets.futures.with_raw_response.get_historical_prices(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_trading_calendar(self, client: Hedgewise) -> None:
        future = client.assets.futures.get_trading_calendar(
            symbol="ZC",
        )
        assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_trading_calendar_with_all_params(self, client: Hedgewise) -> None:
        future = client.assets.futures.get_trading_calendar(
            symbol="ZC",
            end_date="2025-03-18",
            start_date="2025-03-11",
        )
        assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_trading_calendar(self, client: Hedgewise) -> None:
        response = client.assets.futures.with_raw_response.get_trading_calendar(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        future = response.parse()
        assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_trading_calendar(self, client: Hedgewise) -> None:
        with client.assets.futures.with_streaming_response.get_trading_calendar(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            future = response.parse()
            assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_trading_calendar(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            client.assets.futures.with_raw_response.get_trading_calendar(
                symbol="",
            )


class TestAsyncFutures:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncHedgewise) -> None:
        future = await async_client.assets.futures.list()
        assert_matches_type(FutureListResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.assets.futures.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        future = await response.parse()
        assert_matches_type(FutureListResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHedgewise) -> None:
        async with async_client.assets.futures.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            future = await response.parse()
            assert_matches_type(FutureListResponse, future, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_historical_prices(self, async_client: AsyncHedgewise) -> None:
        future = await async_client.assets.futures.get_historical_prices(
            symbol="ZC",
        )
        assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_historical_prices_with_all_params(self, async_client: AsyncHedgewise) -> None:
        future = await async_client.assets.futures.get_historical_prices(
            symbol="ZC",
            active_contracts_only=True,
            back_adjust=True,
            contract="2025H",
            end_date="2025-03-17",
            rollover_method="hist_vol",
            start_date="2025-03-17",
        )
        assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_historical_prices(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.assets.futures.with_raw_response.get_historical_prices(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        future = await response.parse()
        assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_historical_prices(self, async_client: AsyncHedgewise) -> None:
        async with async_client.assets.futures.with_streaming_response.get_historical_prices(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            future = await response.parse()
            assert_matches_type(FutureGetHistoricalPricesResponse, future, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_historical_prices(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            await async_client.assets.futures.with_raw_response.get_historical_prices(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_trading_calendar(self, async_client: AsyncHedgewise) -> None:
        future = await async_client.assets.futures.get_trading_calendar(
            symbol="ZC",
        )
        assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_trading_calendar_with_all_params(self, async_client: AsyncHedgewise) -> None:
        future = await async_client.assets.futures.get_trading_calendar(
            symbol="ZC",
            end_date="2025-03-18",
            start_date="2025-03-11",
        )
        assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_trading_calendar(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.assets.futures.with_raw_response.get_trading_calendar(
            symbol="ZC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        future = await response.parse()
        assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_trading_calendar(self, async_client: AsyncHedgewise) -> None:
        async with async_client.assets.futures.with_streaming_response.get_trading_calendar(
            symbol="ZC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            future = await response.parse()
            assert_matches_type(FutureGetTradingCalendarResponse, future, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_trading_calendar(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            await async_client.assets.futures.with_raw_response.get_trading_calendar(
                symbol="",
            )
