# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AirtopPagination"]


class AirtopPagination(BaseModel):
    current_limit: int = FieldInfo(alias="currentLimit")
    """The number of items to return"""

    current_page: int = FieldInfo(alias="currentPage")
    """The current page number"""

    final_count: int = FieldInfo(alias="finalCount")
    """The final count of items displayed on the current page"""

    has_more: bool = FieldInfo(alias="hasMore")
    """Whether there are more items"""

    initial_count: int = FieldInfo(alias="initialCount")
    """The initial count of items displayed on the current page"""

    next_offset: int = FieldInfo(alias="nextOffset")
    """The number of items to skip"""

    number_of_pages: int = FieldInfo(alias="numberOfPages")
    """The total number of pages"""

    total_items: int = FieldInfo(alias="totalItems")
    """The total number of items"""
