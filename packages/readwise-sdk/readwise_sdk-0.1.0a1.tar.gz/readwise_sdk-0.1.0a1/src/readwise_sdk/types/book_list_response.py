# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["BookListResponse", "Result"]


class Result(BaseModel):
    id: Optional[int] = None
    """Unique identifier for the book"""

    author: Optional[str] = None
    """Author of the book"""

    category: Optional[str] = None
    """Category of the book (e.g., books, articles)"""

    cover_image_url: Optional[str] = None
    """URL of the cover image for the book"""

    last_highlight_at: Optional[datetime] = None
    """Timestamp of the last highlight"""

    num_highlights: Optional[int] = None
    """Number of highlights in the book"""

    source: Optional[str] = None
    """Source identifier"""

    title: Optional[str] = None
    """Title of the book"""

    updated: Optional[datetime] = None
    """Timestamp of the last update"""


class BookListResponse(BaseModel):
    count: Optional[int] = None
    """Total number of books available"""

    next: Optional[str] = None
    """URL to the next page of results"""

    previous: Optional[str] = None
    """URL to the previous page of results"""

    results: Optional[List[Result]] = None
