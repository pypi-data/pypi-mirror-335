# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .scrape_config import ScrapeConfig
from .page_query_experimental_config import PageQueryExperimentalConfig

__all__ = ["PageQueryConfig"]


class PageQueryConfig(TypedDict, total=False):
    experimental: PageQueryExperimentalConfig
    """Experimental configuration options.

    These may be subject to change and are not guaranteed to be stable across
    versions.
    """

    output_schema: Annotated[str, PropertyInfo(alias="outputSchema")]
    """JSON schema defining the structure of the output.

    If not provided, the format of the output might vary.
    """

    scrape: ScrapeConfig
    """Optional configuration to customize and tweak how the web page is scraped."""
