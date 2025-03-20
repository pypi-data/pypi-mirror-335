# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .external_session_config import ExternalSessionConfig

__all__ = ["ExternalSessionWithConnectionInfo"]


class ExternalSessionWithConnectionInfo(BaseModel):
    id: str
    """Id of the session."""

    configuration: ExternalSessionConfig
    """Session configuration details. DEPRECATED"""

    status: str
    """Session status."""

    cdp_url: Optional[str] = FieldInfo(alias="cdpUrl", default=None)
    """Url to connect to chrome devtools protocol port on the Airtop browser.

    Include the header 'Authorization: Bearer <api-key>.'
    """

    cdp_ws_url: Optional[str] = FieldInfo(alias="cdpWsUrl", default=None)
    """
    Websocket url to connect to the Airtop browser for CDP-based automation
    frameworks (e.g. Puppeteer or Playwright). Include the header 'Authorization:
    Bearer <airtop-api-key>.'
    """

    chromedriver_url: Optional[str] = FieldInfo(alias="chromedriverUrl", default=None)
    """
    Websocket url to connect to the Airtop browser for webdriver-based automation
    frameworks (e.g. Selenium). Include the header 'Authorization: Bearer
    <airtop-api-key>.'
    """

    current_usage: Optional[int] = FieldInfo(alias="currentUsage", default=None)
    """Current usage in minutes."""

    date_created: Optional[datetime] = FieldInfo(alias="dateCreated", default=None)
    """Date the session was created."""

    last_activity: Optional[datetime] = FieldInfo(alias="lastActivity", default=None)
    """Date of the last activity."""

    profile_id: Optional[str] = FieldInfo(alias="profileId", default=None)
    """Id of a newly persisted profile. DEPRECATED: Use profileName."""
