# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from readwise_sdk import ReadwiseSDK, AsyncReadwiseSDK
from readwise_sdk.types import BookListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBooks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: ReadwiseSDK) -> None:
        book = client.books.list()
        assert_matches_type(BookListResponse, book, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: ReadwiseSDK) -> None:
        book = client.books.list(
            page=0,
            page_size=1000,
        )
        assert_matches_type(BookListResponse, book, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: ReadwiseSDK) -> None:
        response = client.books.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        book = response.parse()
        assert_matches_type(BookListResponse, book, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: ReadwiseSDK) -> None:
        with client.books.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            book = response.parse()
            assert_matches_type(BookListResponse, book, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBooks:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncReadwiseSDK) -> None:
        book = await async_client.books.list()
        assert_matches_type(BookListResponse, book, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncReadwiseSDK) -> None:
        book = await async_client.books.list(
            page=0,
            page_size=1000,
        )
        assert_matches_type(BookListResponse, book, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncReadwiseSDK) -> None:
        response = await async_client.books.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        book = await response.parse()
        assert_matches_type(BookListResponse, book, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncReadwiseSDK) -> None:
        async with async_client.books.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            book = await response.parse()
            assert_matches_type(BookListResponse, book, path=["response"])

        assert cast(Any, response.is_closed) is True
