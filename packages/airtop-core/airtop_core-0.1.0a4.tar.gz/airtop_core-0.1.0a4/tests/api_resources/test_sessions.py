# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from airtop_core import Airtop, AsyncAirtop
from tests.utils import assert_matches_type
from airtop_core.types.shared import SessionResponse, SessionsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Airtop) -> None:
        session = client.sessions.create()
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Airtop) -> None:
        session = client.sessions.create(
            configuration={
                "base_profile_id": "a13c6f73-bd89-4a76-ab32-5a6c422e8224",
                "extension_ids": ["string"],
                "persist_profile": True,
                "profile_name": "a13c6f73-bd89-4a76-ab32-5a6c422e8224",
                "proxy": True,
                "timeout_minutes": 10,
            },
        )
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Airtop) -> None:
        response = client.sessions.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Airtop) -> None:
        with client.sessions.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Airtop) -> None:
        session = client.sessions.list()
        assert_matches_type(SessionsResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Airtop) -> None:
        session = client.sessions.list(
            limit=10,
            offset=1,
            session_ids=["6aac6f73-bd89-4a76-ab32-5a6c422e8b0b", "e39522ce-44f0-456f-9efd-07b3d4fdd9f2"],
            status="awaitingCapacity",
        )
        assert_matches_type(SessionsResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Airtop) -> None:
        response = client.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionsResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Airtop) -> None:
        with client.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionsResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Airtop) -> None:
        session = client.sessions.get(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Airtop) -> None:
        response = client.sessions.with_raw_response.get(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Airtop) -> None:
        with client.sessions.with_streaming_response.get(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    def test_method_get_events(self, client: Airtop) -> None:
        session_stream = client.sessions.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        session_stream.response.close()

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    def test_method_get_events_with_all_params(self, client: Airtop) -> None:
        session_stream = client.sessions.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
            all=True,
            last_event_id=0,
        )
        session_stream.response.close()

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    def test_raw_response_get_events(self, client: Airtop) -> None:
        response = client.sessions.with_raw_response.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    def test_streaming_response_get_events(self, client: Airtop) -> None:
        with client.sessions.with_streaming_response.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    def test_path_params_get_events(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.get_events(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_save_profile_on_termination(self, client: Airtop) -> None:
        session = client.sessions.save_profile_on_termination(
            profile_name="myProfile",
            session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_save_profile_on_termination(self, client: Airtop) -> None:
        response = client.sessions.with_raw_response.save_profile_on_termination(
            profile_name="myProfile",
            session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_save_profile_on_termination(self, client: Airtop) -> None:
        with client.sessions.with_streaming_response.save_profile_on_termination(
            profile_name="myProfile",
            session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_save_profile_on_termination(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.sessions.with_raw_response.save_profile_on_termination(
                profile_name="myProfile",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `profile_name` but received ''"):
            client.sessions.with_raw_response.save_profile_on_termination(
                profile_name="",
                session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_terminate(self, client: Airtop) -> None:
        session = client.sessions.terminate(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_terminate(self, client: Airtop) -> None:
        response = client.sessions.with_raw_response.terminate(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_terminate(self, client: Airtop) -> None:
        with client.sessions.with_streaming_response.terminate(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_terminate(self, client: Airtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.terminate(
                "",
            )


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncAirtop) -> None:
        session = await async_client.sessions.create()
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAirtop) -> None:
        session = await async_client.sessions.create(
            configuration={
                "base_profile_id": "a13c6f73-bd89-4a76-ab32-5a6c422e8224",
                "extension_ids": ["string"],
                "persist_profile": True,
                "profile_name": "a13c6f73-bd89-4a76-ab32-5a6c422e8224",
                "proxy": True,
                "timeout_minutes": 10,
            },
        )
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAirtop) -> None:
        response = await async_client.sessions.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAirtop) -> None:
        async with async_client.sessions.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncAirtop) -> None:
        session = await async_client.sessions.list()
        assert_matches_type(SessionsResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAirtop) -> None:
        session = await async_client.sessions.list(
            limit=10,
            offset=1,
            session_ids=["6aac6f73-bd89-4a76-ab32-5a6c422e8b0b", "e39522ce-44f0-456f-9efd-07b3d4fdd9f2"],
            status="awaitingCapacity",
        )
        assert_matches_type(SessionsResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAirtop) -> None:
        response = await async_client.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionsResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAirtop) -> None:
        async with async_client.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionsResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncAirtop) -> None:
        session = await async_client.sessions.get(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncAirtop) -> None:
        response = await async_client.sessions.with_raw_response.get(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionResponse, session, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncAirtop) -> None:
        async with async_client.sessions.with_streaming_response.get(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    async def test_method_get_events(self, async_client: AsyncAirtop) -> None:
        session_stream = await async_client.sessions.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    async def test_method_get_events_with_all_params(self, async_client: AsyncAirtop) -> None:
        session_stream = await async_client.sessions.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
            all=True,
            last_event_id=0,
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    async def test_raw_response_get_events(self, async_client: AsyncAirtop) -> None:
        response = await async_client.sessions.with_raw_response.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    async def test_streaming_response_get_events(self, async_client: AsyncAirtop) -> None:
        async with async_client.sessions.with_streaming_response.get_events(
            id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(
        reason="currently no good way to test endpoints with content type text/event-stream, Prism mock server will fail"
    )
    @parametrize
    async def test_path_params_get_events(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.get_events(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_save_profile_on_termination(self, async_client: AsyncAirtop) -> None:
        session = await async_client.sessions.save_profile_on_termination(
            profile_name="myProfile",
            session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_save_profile_on_termination(self, async_client: AsyncAirtop) -> None:
        response = await async_client.sessions.with_raw_response.save_profile_on_termination(
            profile_name="myProfile",
            session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_save_profile_on_termination(self, async_client: AsyncAirtop) -> None:
        async with async_client.sessions.with_streaming_response.save_profile_on_termination(
            profile_name="myProfile",
            session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_save_profile_on_termination(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.sessions.with_raw_response.save_profile_on_termination(
                profile_name="myProfile",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `profile_name` but received ''"):
            await async_client.sessions.with_raw_response.save_profile_on_termination(
                profile_name="",
                session_id="6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_terminate(self, async_client: AsyncAirtop) -> None:
        session = await async_client.sessions.terminate(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_terminate(self, async_client: AsyncAirtop) -> None:
        response = await async_client.sessions.with_raw_response.terminate(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert session is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_terminate(self, async_client: AsyncAirtop) -> None:
        async with async_client.sessions.with_streaming_response.terminate(
            "6aac6f73-bd89-4a76-ab32-5a6c422e8b0b",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_terminate(self, async_client: AsyncAirtop) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.terminate(
                "",
            )
