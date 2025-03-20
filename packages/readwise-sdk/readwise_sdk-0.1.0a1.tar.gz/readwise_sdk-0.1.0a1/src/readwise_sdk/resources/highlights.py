# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import highlight_list_params
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
from ..types.highlight_list_response import HighlightListResponse

__all__ = ["HighlightsResource", "AsyncHighlightsResource"]


class HighlightsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HighlightsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return HighlightsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HighlightsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#with_streaming_response
        """
        return HighlightsResourceWithStreamingResponse(self)

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
    ) -> HighlightListResponse:
        """
        Retrieves a paginated list of highlights.

        Args:
          page: Pagination counter

          page_size: Number of results per page (maximum 1000)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/highlights/",
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
                    highlight_list_params.HighlightListParams,
                ),
            ),
            cast_to=HighlightListResponse,
        )


class AsyncHighlightsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHighlightsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncHighlightsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHighlightsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/rexledesma/readwise-sdk-python#with_streaming_response
        """
        return AsyncHighlightsResourceWithStreamingResponse(self)

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
    ) -> HighlightListResponse:
        """
        Retrieves a paginated list of highlights.

        Args:
          page: Pagination counter

          page_size: Number of results per page (maximum 1000)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/highlights/",
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
                    highlight_list_params.HighlightListParams,
                ),
            ),
            cast_to=HighlightListResponse,
        )


class HighlightsResourceWithRawResponse:
    def __init__(self, highlights: HighlightsResource) -> None:
        self._highlights = highlights

        self.list = to_raw_response_wrapper(
            highlights.list,
        )


class AsyncHighlightsResourceWithRawResponse:
    def __init__(self, highlights: AsyncHighlightsResource) -> None:
        self._highlights = highlights

        self.list = async_to_raw_response_wrapper(
            highlights.list,
        )


class HighlightsResourceWithStreamingResponse:
    def __init__(self, highlights: HighlightsResource) -> None:
        self._highlights = highlights

        self.list = to_streamed_response_wrapper(
            highlights.list,
        )


class AsyncHighlightsResourceWithStreamingResponse:
    def __init__(self, highlights: AsyncHighlightsResource) -> None:
        self._highlights = highlights

        self.list = async_to_streamed_response_wrapper(
            highlights.list,
        )
