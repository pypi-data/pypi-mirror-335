# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .scrape_response_output import ScrapeResponseOutput

__all__ = ["ScrapeResponseEnvelope"]


class ScrapeResponseEnvelope(BaseModel):
    api_model_response: ScrapeResponseOutput = FieldInfo(alias="modelResponse")
    """The response from the Airtop AI model."""
