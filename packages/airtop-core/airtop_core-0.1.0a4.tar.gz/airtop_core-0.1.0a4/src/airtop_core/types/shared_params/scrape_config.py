# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ScrapeConfig"]


class ScrapeConfig(TypedDict, total=False):
    optimize_urls: Annotated[str, PropertyInfo(alias="optimizeUrls")]
    """
    URL optimization helps improve performance during model analysis, but limits the
    model's ability to analyze internal details of URLs (such as individual URL
    parameters). This setting does not affect the ability to extract URLs or links
    from web pages -- those will work regardless of how this option is set. However,
    if you need to analyze URLs themselves and are not getting satisfactory results,
    try setting this option to 'disabled'. If set to 'auto', Airtop AI will
    automatically determine whether to apply URL optimization. If 'enabled', URLs
    will always be optimized to improve performance. If 'disabled', URLs will not be
    optimized.
    """
