# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from airtop_core import Airtop, AsyncAirtop
from tests.utils import assert_matches_type
from airtop_core.types.shared import ProfileOutput

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProfile:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Airtop) -> None:
        profile = client.profile.delete()
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_with_all_params(self, client: Airtop) -> None:
        profile = client.profile.delete(
            profile_ids=["abc", "123"],
            profile_names=["abc", "123"],
        )
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Airtop) -> None:
        response = client.profile.with_raw_response.delete()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = response.parse()
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Airtop) -> None:
        with client.profile.with_streaming_response.delete() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = response.parse()
            assert profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Airtop) -> None:
        profile = client.profile.get(
            "my-profile",
        )
        assert_matches_type(ProfileOutput, profile, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Airtop) -> None:
        response = client.profile.with_raw_response.get(
            "my-profile",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = response.parse()
        assert_matches_type(ProfileOutput, profile, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Airtop) -> None:
        with client.profile.with_streaming_response.get(
            "my-profile",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = response.parse()
            assert_matches_type(ProfileOutput, profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.profile.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_rename(self, client: Airtop) -> None:
        profile = client.profile.rename(
            source="oldProfile",
            target="newProfile",
        )
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    def test_method_rename_with_all_params(self, client: Airtop) -> None:
        profile = client.profile.rename(
            source="oldProfile",
            target="newProfile",
            force=True,
        )
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_rename(self, client: Airtop) -> None:
        response = client.profile.with_raw_response.rename(
            source="oldProfile",
            target="newProfile",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = response.parse()
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_rename(self, client: Airtop) -> None:
        with client.profile.with_streaming_response.rename(
            source="oldProfile",
            target="newProfile",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = response.parse()
            assert profile is None

        assert cast(Any, response.is_closed) is True


class TestAsyncProfile:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncAirtop) -> None:
        profile = await async_client.profile.delete()
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncAirtop) -> None:
        profile = await async_client.profile.delete(
            profile_ids=["abc", "123"],
            profile_names=["abc", "123"],
        )
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAirtop) -> None:
        response = await async_client.profile.with_raw_response.delete()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = await response.parse()
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAirtop) -> None:
        async with async_client.profile.with_streaming_response.delete() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = await response.parse()
            assert profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncAirtop) -> None:
        profile = await async_client.profile.get(
            "my-profile",
        )
        assert_matches_type(ProfileOutput, profile, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncAirtop) -> None:
        response = await async_client.profile.with_raw_response.get(
            "my-profile",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = await response.parse()
        assert_matches_type(ProfileOutput, profile, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncAirtop) -> None:
        async with async_client.profile.with_streaming_response.get(
            "my-profile",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = await response.parse()
            assert_matches_type(ProfileOutput, profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.profile.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_rename(self, async_client: AsyncAirtop) -> None:
        profile = await async_client.profile.rename(
            source="oldProfile",
            target="newProfile",
        )
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_rename_with_all_params(self, async_client: AsyncAirtop) -> None:
        profile = await async_client.profile.rename(
            source="oldProfile",
            target="newProfile",
            force=True,
        )
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_rename(self, async_client: AsyncAirtop) -> None:
        response = await async_client.profile.with_raw_response.rename(
            source="oldProfile",
            target="newProfile",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        profile = await response.parse()
        assert profile is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_rename(self, async_client: AsyncAirtop) -> None:
        async with async_client.profile.with_streaming_response.rename(
            source="oldProfile",
            target="newProfile",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            profile = await response.parse()
            assert profile is None

        assert cast(Any, response.is_closed) is True
