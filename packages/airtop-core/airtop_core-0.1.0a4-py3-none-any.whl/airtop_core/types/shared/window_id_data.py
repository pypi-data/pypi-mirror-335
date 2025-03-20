# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["WindowIDData"]


class WindowIDData(BaseModel):
    target_id: str = FieldInfo(alias="targetId")
    """CDP Window target ID"""

    window_id: str = FieldInfo(alias="windowId")
    """Airtop window ID of the browser window"""
