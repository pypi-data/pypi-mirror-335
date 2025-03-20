# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["WindowInfo"]


class WindowInfo(BaseModel):
    live_view_url: str = FieldInfo(alias="liveViewUrl")
    """
    Url for loading a browser window live view that is configured according to the
    request options like screenResolution, disableResize, etc.
    """

    target_id: str = FieldInfo(alias="targetId")
    """CDP target ID of the browser window"""

    window_id: str = FieldInfo(alias="windowId")
    """Airtop window ID of the browser window"""
