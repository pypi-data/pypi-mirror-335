# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from airtop_core import Airtop, AsyncAirtop
from tests.utils import assert_matches_type
from airtop_core.types.shared import AutomationData, ListAutomationsOutput

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAutomations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Airtop) -> None:
        automation = client.automations.list()
        assert_matches_type(ListAutomationsOutput, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Airtop) -> None:
        response = client.automations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(ListAutomationsOutput, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Airtop) -> None:
        with client.automations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(ListAutomationsOutput, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Airtop) -> None:
        automation = client.automations.delete(
            "automationId",
        )
        assert_matches_type(object, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Airtop) -> None:
        response = client.automations.with_raw_response.delete(
            "automationId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(object, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Airtop) -> None:
        with client.automations.with_streaming_response.delete(
            "automationId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(object, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.automations.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Airtop) -> None:
        automation = client.automations.get(
            "automationId",
        )
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Airtop) -> None:
        response = client.automations.with_raw_response.get(
            "automationId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Airtop) -> None:
        with client.automations.with_streaming_response.get(
            "automationId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(AutomationData, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.automations.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_description(self, client: Airtop) -> None:
        automation = client.automations.update_description(
            id="id",
            description="description",
            org_id="orgId",
        )
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_description(self, client: Airtop) -> None:
        response = client.automations.with_raw_response.update_description(
            id="id",
            description="description",
            org_id="orgId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_description(self, client: Airtop) -> None:
        with client.automations.with_streaming_response.update_description(
            id="id",
            description="description",
            org_id="orgId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(AutomationData, automation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAutomations:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncAirtop) -> None:
        automation = await async_client.automations.list()
        assert_matches_type(ListAutomationsOutput, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAirtop) -> None:
        response = await async_client.automations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = await response.parse()
        assert_matches_type(ListAutomationsOutput, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAirtop) -> None:
        async with async_client.automations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(ListAutomationsOutput, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncAirtop) -> None:
        automation = await async_client.automations.delete(
            "automationId",
        )
        assert_matches_type(object, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAirtop) -> None:
        response = await async_client.automations.with_raw_response.delete(
            "automationId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = await response.parse()
        assert_matches_type(object, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAirtop) -> None:
        async with async_client.automations.with_streaming_response.delete(
            "automationId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(object, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.automations.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncAirtop) -> None:
        automation = await async_client.automations.get(
            "automationId",
        )
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncAirtop) -> None:
        response = await async_client.automations.with_raw_response.get(
            "automationId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = await response.parse()
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncAirtop) -> None:
        async with async_client.automations.with_streaming_response.get(
            "automationId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(AutomationData, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.automations.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_description(self, async_client: AsyncAirtop) -> None:
        automation = await async_client.automations.update_description(
            id="id",
            description="description",
            org_id="orgId",
        )
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_description(self, async_client: AsyncAirtop) -> None:
        response = await async_client.automations.with_raw_response.update_description(
            id="id",
            description="description",
            org_id="orgId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = await response.parse()
        assert_matches_type(AutomationData, automation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_description(self, async_client: AsyncAirtop) -> None:
        async with async_client.automations.with_streaming_response.update_description(
            id="id",
            description="description",
            org_id="orgId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(AutomationData, automation, path=["response"])

        assert cast(Any, response.is_closed) is True
