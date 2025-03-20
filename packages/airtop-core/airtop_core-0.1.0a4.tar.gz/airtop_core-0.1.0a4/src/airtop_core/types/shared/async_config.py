# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AsyncConfig"]


class AsyncConfig(BaseModel):
    webhook_url: Optional[str] = FieldInfo(alias="webhookUrl", default=None)
    """The URL to send the response to when the request is complete."""
