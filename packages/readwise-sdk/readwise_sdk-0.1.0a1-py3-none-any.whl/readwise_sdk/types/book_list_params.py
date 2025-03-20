# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["BookListParams"]


class BookListParams(TypedDict, total=False):
    page: int
    """Pagination counter"""

    page_size: int
    """Number of results per page (maximum 1000)"""
