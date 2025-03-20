# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from ..._models import BaseModel

__all__ = ["ErrorBody"]


class ErrorBody(BaseModel):
    code: str
    """Error code"""

    message: str
    """Error message"""
