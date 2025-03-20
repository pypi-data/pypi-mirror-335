# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["FileCreateFileParams"]


class FileCreateFileParams(TypedDict, total=False):
    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
    """Name of the file"""

    file_type: Annotated[
        Literal["browser_download", "screenshot", "video", "customer_upload"], PropertyInfo(alias="fileType")
    ]
    """Type of the file"""

    session_id: Annotated[str, PropertyInfo(alias="sessionId")]
    """ID of the session"""
