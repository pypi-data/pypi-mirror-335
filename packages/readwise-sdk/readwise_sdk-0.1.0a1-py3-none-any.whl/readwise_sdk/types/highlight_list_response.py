# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["HighlightListResponse", "Result", "ResultTag"]


class ResultTag(BaseModel):
    id: Optional[int] = None
    """Unique identifier for the tag"""

    name: Optional[str] = None
    """Name of the tag"""


class Result(BaseModel):
    id: Optional[int] = None
    """Unique identifier for the highlight"""

    book_id: Optional[int] = None
    """Identifier of the associated book"""

    highlighted_at: Optional[datetime] = None
    """Timestamp of when the highlight was taken"""

    location: Optional[int] = None
    """Highlight's location in the source text"""

    location_type: Optional[str] = None
    """Type of location (e.g., page, order, time_offset)"""

    note: Optional[str] = None
    """Annotation note attached to the highlight"""

    tags: Optional[List[ResultTag]] = None

    text: Optional[str] = None
    """The highlight text"""

    url: Optional[str] = None
    """URL of the highlight"""


class HighlightListResponse(BaseModel):
    count: Optional[int] = None
    """Total number of highlights available"""

    next: Optional[str] = None
    """URL to the next page of results"""

    previous: Optional[str] = None
    """URL to the previous page of results"""

    results: Optional[List[Result]] = None
