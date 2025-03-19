# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types import SupplyListResponse, SupplyRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSupply:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Hedgewise) -> None:
        supply = client.supply.retrieve(
            symbol="KC",
        )
        assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Hedgewise) -> None:
        supply = client.supply.retrieve(
            symbol="KC",
            country_code="BR",
            end_date="2025-03-18",
            get_feature_contributions=True,
            model="v2_wholecountry_92to23_interval10_yesyoy_xgb",
            start_date="2024-03-18",
        )
        assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Hedgewise) -> None:
        response = client.supply.with_raw_response.retrieve(
            symbol="KC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supply = response.parse()
        assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Hedgewise) -> None:
        with client.supply.with_streaming_response.retrieve(
            symbol="KC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supply = response.parse()
            assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            client.supply.with_raw_response.retrieve(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Hedgewise) -> None:
        supply = client.supply.list()
        assert_matches_type(SupplyListResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Hedgewise) -> None:
        response = client.supply.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supply = response.parse()
        assert_matches_type(SupplyListResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Hedgewise) -> None:
        with client.supply.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supply = response.parse()
            assert_matches_type(SupplyListResponse, supply, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSupply:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncHedgewise) -> None:
        supply = await async_client.supply.retrieve(
            symbol="KC",
        )
        assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncHedgewise) -> None:
        supply = await async_client.supply.retrieve(
            symbol="KC",
            country_code="BR",
            end_date="2025-03-18",
            get_feature_contributions=True,
            model="v2_wholecountry_92to23_interval10_yesyoy_xgb",
            start_date="2024-03-18",
        )
        assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.supply.with_raw_response.retrieve(
            symbol="KC",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supply = await response.parse()
        assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncHedgewise) -> None:
        async with async_client.supply.with_streaming_response.retrieve(
            symbol="KC",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supply = await response.parse()
            assert_matches_type(SupplyRetrieveResponse, supply, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `symbol` but received ''"):
            await async_client.supply.with_raw_response.retrieve(
                symbol="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncHedgewise) -> None:
        supply = await async_client.supply.list()
        assert_matches_type(SupplyListResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.supply.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supply = await response.parse()
        assert_matches_type(SupplyListResponse, supply, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHedgewise) -> None:
        async with async_client.supply.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supply = await response.parse()
            assert_matches_type(SupplyListResponse, supply, path=["response"])

        assert cast(Any, response.is_closed) is True
