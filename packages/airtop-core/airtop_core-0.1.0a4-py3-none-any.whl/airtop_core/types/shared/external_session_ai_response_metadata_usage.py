# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from ..._models import BaseModel

__all__ = ["ExternalSessionAIResponseMetadataUsage"]


class ExternalSessionAIResponseMetadataUsage(BaseModel):
    id: str
    """The id of the request"""

    credits: int
    """The credit usage for this request"""
