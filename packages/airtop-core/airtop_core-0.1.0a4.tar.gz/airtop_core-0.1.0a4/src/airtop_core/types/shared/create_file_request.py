# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CreateFileRequest"]


class CreateFileRequest(BaseModel):
    file_name: str = FieldInfo(alias="fileName")
    """Name of the file"""

    file_type: Optional[Literal["browser_download", "screenshot", "video", "customer_upload"]] = FieldInfo(
        alias="fileType", default=None
    )
    """Type of the file"""

    session_id: Optional[str] = FieldInfo(alias="sessionId", default=None)
    """ID of the session"""
