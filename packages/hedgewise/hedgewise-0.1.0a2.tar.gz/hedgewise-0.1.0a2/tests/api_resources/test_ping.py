# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hedgewise import Hedgewise, AsyncHedgewise
from tests.utils import assert_matches_type
from hedgewise.types import PingPingResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPing:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_ping(self, client: Hedgewise) -> None:
        ping = client.ping.ping()
        assert_matches_type(PingPingResponse, ping, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_ping(self, client: Hedgewise) -> None:
        response = client.ping.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ping = response.parse()
        assert_matches_type(PingPingResponse, ping, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_ping(self, client: Hedgewise) -> None:
        with client.ping.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ping = response.parse()
            assert_matches_type(PingPingResponse, ping, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPing:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_ping(self, async_client: AsyncHedgewise) -> None:
        ping = await async_client.ping.ping()
        assert_matches_type(PingPingResponse, ping, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_ping(self, async_client: AsyncHedgewise) -> None:
        response = await async_client.ping.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ping = await response.parse()
        assert_matches_type(PingPingResponse, ping, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_ping(self, async_client: AsyncHedgewise) -> None:
        async with async_client.ping.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ping = await response.parse()
            assert_matches_type(PingPingResponse, ping, path=["response"])

        assert cast(Any, response.is_closed) is True
