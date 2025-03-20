# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from ..._models import BaseModel

__all__ = ["OperationOutcome"]


class OperationOutcome(BaseModel):
    success: bool
    """Indicates if the operations was successful"""
