# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .shared_params.session_config_v1 import SessionConfigV1

__all__ = ["SessionCreateParams"]


class SessionCreateParams(TypedDict, total=False):
    configuration: SessionConfigV1
    """Session configuration"""
