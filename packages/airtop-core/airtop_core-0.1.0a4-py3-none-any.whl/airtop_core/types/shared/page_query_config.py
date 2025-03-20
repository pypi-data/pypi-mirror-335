# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .scrape_config import ScrapeConfig
from .page_query_experimental_config import PageQueryExperimentalConfig

__all__ = ["PageQueryConfig"]


class PageQueryConfig(BaseModel):
    experimental: Optional[PageQueryExperimentalConfig] = None
    """Experimental configuration options.

    These may be subject to change and are not guaranteed to be stable across
    versions.
    """

    output_schema: Optional[str] = FieldInfo(alias="outputSchema", default=None)
    """JSON schema defining the structure of the output.

    If not provided, the format of the output might vary.
    """

    scrape: Optional[ScrapeConfig] = None
    """Optional configuration to customize and tweak how the web page is scraped."""
