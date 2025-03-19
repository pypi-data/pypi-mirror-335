# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types import ForexListResponse, ForexRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestForex:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Hedgewise) -> None:
        forex = client.forex.retrieve(
            code="EUR",
        )
        assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Hedgewise) -> None:
        forex = client.forex.retrieve(
            code="EUR",
            end_date="2025-03-18",
            foreign_per_usd=True,
            start_date="2025-03-11",
        )
        assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Hedgewise) -> None:
        response = client.forex.with_raw_response.retrieve(
            code="EUR",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forex = response.parse()
        assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Hedgewise) -> None:
        with client.forex.with_streaming_response.retrieve(
            code="EUR",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forex = response.parse()
            assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Hedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `code` but received ''"):
            client.forex.with_raw_response.retrieve(
                code="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Hedgewise) -> None:
        forex = client.forex.list()
        assert_matches_type(ForexListResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Hedgewise) -> None:
        response = client.forex.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forex = response.parse()
        assert_matches_type(ForexListResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Hedgewise) -> None:
        with client.forex.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forex = response.parse()
            assert_matches_type(ForexListResponse, forex, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncForex:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncHedgewise) -> None:
        forex = await async_client.forex.retrieve(
            code="EUR",
        )
        assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncHedgewise) -> None:
        forex = await async_client.forex.retrieve(
            code="EUR",
            end_date="2025-03-18",
            foreign_per_usd=True,
            start_date="2025-03-11",
        )
        assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.forex.with_raw_response.retrieve(
            code="EUR",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forex = await response.parse()
        assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncHedgewise) -> None:
        async with async_client.forex.with_streaming_response.retrieve(
            code="EUR",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forex = await response.parse()
            assert_matches_type(ForexRetrieveResponse, forex, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncHedgewise) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `code` but received ''"):
            await async_client.forex.with_raw_response.retrieve(
                code="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncHedgewise) -> None:
        forex = await async_client.forex.list()
        assert_matches_type(ForexListResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.forex.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        forex = await response.parse()
        assert_matches_type(ForexListResponse, forex, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHedgewise) -> None:
        async with async_client.forex.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            forex = await response.parse()
            assert_matches_type(ForexListResponse, forex, path=["response"])

        assert cast(Any, response.is_closed) is True
