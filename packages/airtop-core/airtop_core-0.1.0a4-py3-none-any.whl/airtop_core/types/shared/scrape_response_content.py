# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ScrapeResponseContent"]


class ScrapeResponseContent(BaseModel):
    content_type: str = FieldInfo(alias="contentType")
    """
    The mime type of content extracted from the browser window (usually text/plain
    but could be text/csv or other types depending on the site).
    """

    text: str
    """The text content of the browser window."""
