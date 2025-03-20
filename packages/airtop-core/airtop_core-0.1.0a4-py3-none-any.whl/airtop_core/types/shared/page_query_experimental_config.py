# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["PageQueryExperimentalConfig"]


class PageQueryExperimentalConfig(BaseModel):
    include_visual_analysis: Optional[str] = FieldInfo(alias="includeVisualAnalysis", default=None)
    """
    If set to 'enabled', Airtop AI will also analyze the web page visually when
    fulfilling the request. Note that this can add to both the execution time and
    cost of the operation. If the page is too large, the context window can be
    exceeded and the request will fail. If set to 'auto' or 'disabled', no visual
    analysis will be conducted. If 'followPaginationLinks' is set to true, visual
    analysis will be conducted unless 'includeVisualAnalysis' is explicitly set to
    'disabled'.
    """
