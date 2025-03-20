# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .scrape_config import ScrapeConfig

__all__ = ["PaginatedExtractionConfig", "Experimental"]


class Experimental(TypedDict, total=False):
    scroll_within: Annotated[str, PropertyInfo(alias="scrollWithin")]
    """A natural language description of the scrollable area on the web page.

    This identifies the container or region that should be scrolled to access
    pagination controls. If missing, the entire page will be scrolled. You can also
    describe a visible reference point inside the container.
    """


class PaginatedExtractionConfig(TypedDict, total=False):
    experimental: Experimental
    """Experimental configuration options.

    These may be subject to change and are not guaranteed to be stable across
    versions.
    """

    interaction_mode: Annotated[str, PropertyInfo(alias="interactionMode")]
    """The mode to use for interaction.

    If set to 'auto', Airtop AI will automatically choose the most cost-effective
    interaction mode. If set to 'accurate', the request might be slower, but more
    likely to be accurate. Whereas, 'cost-efficient' will be cheaper and speed
    things up, but may reduce accuracy.
    """

    output_schema: Annotated[str, PropertyInfo(alias="outputSchema")]
    """JSON schema defining the structure of the output.

    If not provided, the format of the output might vary.
    """

    pagination_mode: Annotated[str, PropertyInfo(alias="paginationMode")]
    """The mode to use for pagination.

    If set to 'auto', Airtop AI will automatically look for pagination links first
    and then attempt infinite scrolling to load more content. If set to 'paginated',
    Airtop AI will follow pagination links to load more content. If set to
    'infinite-scroll', Airtop AI will scroll the page to load more content.
    """

    scrape: ScrapeConfig
    """Optional configuration to customize and tweak how the web page is scraped."""
