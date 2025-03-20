# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from ..._models import BaseModel

__all__ = ["ErrorMessage"]


class ErrorMessage(BaseModel):
    code: str
    """Error code"""

    event: str
    """Event name"""

    message: str
    """Error message"""
