# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .issue import Issue
from ..._models import BaseModel
from .scrape_response_envelope import ScrapeResponseEnvelope
from .external_session_ai_response_metadata import ExternalSessionAIResponseMetadata

__all__ = ["ScrapeResponse"]


class ScrapeResponse(BaseModel):
    data: ScrapeResponseEnvelope

    errors: Optional[List[Issue]] = None

    meta: ExternalSessionAIResponseMetadata

    warnings: Optional[List[Issue]] = None
