# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .issue import Issue
from ..._models import BaseModel
from .ai_response_envelope import AIResponseEnvelope
from .external_session_ai_response_metadata import ExternalSessionAIResponseMetadata

__all__ = ["AIPromptResponse"]


class AIPromptResponse(BaseModel):
    data: AIResponseEnvelope

    errors: Optional[List[Issue]] = None

    meta: ExternalSessionAIResponseMetadata

    warnings: Optional[List[Issue]] = None
