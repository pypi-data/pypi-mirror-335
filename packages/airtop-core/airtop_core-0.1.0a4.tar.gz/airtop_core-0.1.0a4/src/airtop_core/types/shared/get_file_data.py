# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GetFileData"]


class GetFileData(BaseModel):
    id: str
    """ID of the file"""

    download_url: str = FieldInfo(alias="downloadUrl")
    """URL to download the file"""

    file_bytes: int = FieldInfo(alias="fileBytes")
    """Size of the file in bytes"""

    file_name: str = FieldInfo(alias="fileName")
    """Name of the file"""

    file_type: Literal["browser_download", "screenshot", "video", "customer_upload"] = FieldInfo(alias="fileType")
    """Type of the file"""

    org_id: str = FieldInfo(alias="orgId")
    """ID of the organization"""

    uploaded_at: datetime = FieldInfo(alias="uploadedAt")
    """Time when the file was uploaded"""

    session_id: Optional[str] = FieldInfo(alias="sessionId", default=None)
    """ID of the session"""
