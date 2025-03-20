# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AIResponseEnvelope"]


class AIResponseEnvelope(BaseModel):
    ai_model_response: str = FieldInfo(alias="modelResponse")
