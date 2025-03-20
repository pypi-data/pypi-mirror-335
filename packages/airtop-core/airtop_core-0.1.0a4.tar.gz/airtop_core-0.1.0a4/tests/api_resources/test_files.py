# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from airtop_core import Airtop, AsyncAirtop
from tests.utils import assert_matches_type
from airtop_core.types.shared import GetFileResponse, CreateFileResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_file(self, client: Airtop) -> None:
        file = client.files.create_file(
            file_name="fileName",
        )
        assert_matches_type(CreateFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_file_with_all_params(self, client: Airtop) -> None:
        file = client.files.create_file(
            file_name="fileName",
            file_type="browser_download",
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CreateFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_file(self, client: Airtop) -> None:
        response = client.files.with_raw_response.create_file(
            file_name="fileName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(CreateFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_file(self, client: Airtop) -> None:
        with client.files.with_streaming_response.create_file(
            file_name="fileName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(CreateFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Airtop) -> None:
        file = client.files.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(GetFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Airtop) -> None:
        response = client.files.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(GetFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Airtop) -> None:
        with client.files.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(GetFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.files.with_raw_response.get(
                "",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_file(self, async_client: AsyncAirtop) -> None:
        file = await async_client.files.create_file(
            file_name="fileName",
        )
        assert_matches_type(CreateFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_file_with_all_params(self, async_client: AsyncAirtop) -> None:
        file = await async_client.files.create_file(
            file_name="fileName",
            file_type="browser_download",
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CreateFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_file(self, async_client: AsyncAirtop) -> None:
        response = await async_client.files.with_raw_response.create_file(
            file_name="fileName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(CreateFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_file(self, async_client: AsyncAirtop) -> None:
        async with async_client.files.with_streaming_response.create_file(
            file_name="fileName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(CreateFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncAirtop) -> None:
        file = await async_client.files.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(GetFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncAirtop) -> None:
        response = await async_client.files.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(GetFileResponse, file, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncAirtop) -> None:
        async with async_client.files.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(GetFileResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.files.with_raw_response.get(
                "",
            )
