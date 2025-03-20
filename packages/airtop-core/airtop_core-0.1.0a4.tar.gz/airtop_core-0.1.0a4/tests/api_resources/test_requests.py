# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from airtop_core import Airtop, AsyncAirtop
from tests.utils import assert_matches_type
from airtop_core.types.shared import RequestStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRequests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_request_status(self, client: Airtop) -> None:
        request = client.requests.get_request_status(
            "123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(RequestStatusResponse, request, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_request_status(self, client: Airtop) -> None:
        response = client.requests.with_raw_response.get_request_status(
            "123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request = response.parse()
        assert_matches_type(RequestStatusResponse, request, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_request_status(self, client: Airtop) -> None:
        with client.requests.with_streaming_response.get_request_status(
            "123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request = response.parse()
            assert_matches_type(RequestStatusResponse, request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_request_status(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `request_id` but received ''"):
            client.requests.with_raw_response.get_request_status(
                "",
            )


class TestAsyncRequests:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_request_status(self, async_client: AsyncAirtop) -> None:
        request = await async_client.requests.get_request_status(
            "123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(RequestStatusResponse, request, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_request_status(self, async_client: AsyncAirtop) -> None:
        response = await async_client.requests.with_raw_response.get_request_status(
            "123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        request = await response.parse()
        assert_matches_type(RequestStatusResponse, request, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_request_status(self, async_client: AsyncAirtop) -> None:
        async with async_client.requests.with_streaming_response.get_request_status(
            "123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            request = await response.parse()
            assert_matches_type(RequestStatusResponse, request, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_request_status(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `request_id` but received ''"):
            await async_client.requests.with_raw_response.get_request_status(
                "",
            )
