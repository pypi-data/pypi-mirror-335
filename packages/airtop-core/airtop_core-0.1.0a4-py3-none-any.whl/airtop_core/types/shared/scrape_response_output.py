# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .scrape_response_content import ScrapeResponseContent

__all__ = ["ScrapeResponseOutput"]


class ScrapeResponseOutput(BaseModel):
    scraped_content: ScrapeResponseContent = FieldInfo(alias="scrapedContent")
    """The scraped content of the browser window."""

    title: str
    """The title of the browser page."""

    selected_text: Optional[str] = FieldInfo(alias="selectedText", default=None)
    """Any text that was highlighted in the browser window."""
