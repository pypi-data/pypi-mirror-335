# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .screenshot_metadata import ScreenshotMetadata
from .client_provided_response_metadata import ClientProvidedResponseMetadata
from .external_session_ai_response_metadata_usage import ExternalSessionAIResponseMetadataUsage

__all__ = ["ExternalSessionAIResponseMetadata"]


class ExternalSessionAIResponseMetadata(BaseModel):
    status: Literal["success", "partial", "failure"]
    """Outcome of the operation."""

    usage: ExternalSessionAIResponseMetadataUsage

    client_provided: Optional[ClientProvidedResponseMetadata] = FieldInfo(alias="clientProvided", default=None)

    request_id: Optional[str] = FieldInfo(alias="requestId", default=None)

    screenshots: Optional[List[ScreenshotMetadata]] = None
    """Array containing any requested screenshots from the operation."""
