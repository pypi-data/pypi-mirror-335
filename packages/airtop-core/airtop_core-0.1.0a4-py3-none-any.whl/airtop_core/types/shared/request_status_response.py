# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from ..._models import BaseModel

__all__ = ["RequestStatusResponse"]


class RequestStatusResponse(BaseModel):
    response: object
    """The response data, if available"""

    status: str
    """The current status of the request (pending, completed, error)"""
