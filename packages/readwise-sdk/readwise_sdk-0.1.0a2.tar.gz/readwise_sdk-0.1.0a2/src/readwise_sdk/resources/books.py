# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import book_list_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.book_list_response import BookListResponse

__all__ = ["BooksResource", "AsyncBooksResource"]


class BooksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return BooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#with_streaming_response
        """
        return BooksResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BookListResponse:
        """
        Retrieves a paginated list of books.

        Args:
          page: Pagination counter

          page_size: Number of results per page (maximum 1000)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/books/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    book_list_params.BookListParams,
                ),
            ),
            cast_to=BookListResponse,
        )


class AsyncBooksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#with_streaming_response
        """
        return AsyncBooksResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BookListResponse:
        """
        Retrieves a paginated list of books.

        Args:
          page: Pagination counter

          page_size: Number of results per page (maximum 1000)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/books/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    book_list_params.BookListParams,
                ),
            ),
            cast_to=BookListResponse,
        )


class BooksResourceWithRawResponse:
    def __init__(self, books: BooksResource) -> None:
        self._books = books

        self.list = to_raw_response_wrapper(
            books.list,
        )


class AsyncBooksResourceWithRawResponse:
    def __init__(self, books: AsyncBooksResource) -> None:
        self._books = books

        self.list = async_to_raw_response_wrapper(
            books.list,
        )


class BooksResourceWithStreamingResponse:
    def __init__(self, books: BooksResource) -> None:
        self._books = books

        self.list = to_streamed_response_wrapper(
            books.list,
        )


class AsyncBooksResourceWithStreamingResponse:
    def __init__(self, books: AsyncBooksResource) -> None:
        self._books = books

        self.list = async_to_streamed_response_wrapper(
            books.list,
        )
