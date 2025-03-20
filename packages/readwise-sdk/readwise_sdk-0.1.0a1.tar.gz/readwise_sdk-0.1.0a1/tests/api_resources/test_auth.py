# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from readwise_sdk import ReadwiseSDK, AsyncReadwiseSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_check(self, client: ReadwiseSDK) -> None:
        auth = client.auth.check()
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_check(self, client: ReadwiseSDK) -> None:
        response = client.auth.with_raw_response.check()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_check(self, client: ReadwiseSDK) -> None:
        with client.auth.with_streaming_response.check() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_check(self, async_client: AsyncReadwiseSDK) -> None:
        auth = await async_client.auth.check()
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_check(self, async_client: AsyncReadwiseSDK) -> None:
        response = await async_client.auth.with_raw_response.check()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_check(self, async_client: AsyncReadwiseSDK) -> None:
        async with async_client.auth.with_streaming_response.check() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True
