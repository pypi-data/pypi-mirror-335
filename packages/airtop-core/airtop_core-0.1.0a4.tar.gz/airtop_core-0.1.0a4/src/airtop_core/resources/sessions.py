# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, List, Optional, cast
from typing_extensions import Literal

import httpx

from ..types import session_list_params, session_create_params, session_get_events_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.shared.session_response import SessionResponse
from ..types.shared.sessions_response import SessionsResponse
from ..types.session_get_events_response import SessionGetEventsResponse
from ..types.shared_params.session_config_v1 import SessionConfigV1

__all__ = ["SessionsResource", "AsyncSessionsResource"]


class SessionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#with_streaming_response
        """
        return SessionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        configuration: SessionConfigV1 | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SessionResponse:
        """
        Create a session

        Args:
          configuration: Session configuration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/sessions",
            body=maybe_transform({"configuration": configuration}, session_create_params.SessionCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionResponse,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        session_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        status: Literal["awaitingCapacity", "initializing", "running", "ended", "completed", "cancelled", "all"]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SessionsResponse:
        """
        Get a list of sessions by ID

        Args:
          limit: Limit for pagination.

          offset: Offset for pagination.

          session_ids: A comma-separated list of IDs of the sessions to retrieve.

          status: Status of the session to get.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "session_ids": session_ids,
                        "status": status,
                    },
                    session_list_params.SessionListParams,
                ),
            ),
            cast_to=SessionsResponse,
        )

    def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SessionResponse:
        """
        Get a session by ID

        Args:
          id: Id of the session to get

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/sessions/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionResponse,
        )

    def get_events(
        self,
        id: str,
        *,
        all: bool | NotGiven = NOT_GIVEN,
        last_event_id: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[SessionGetEventsResponse]:
        """
        Get a session event stream for a given session ID

        Args:
          id: ID of the session to get status info for

          all: Get all events

          last_event_id: last known event id

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        return self._get(
            f"/sessions/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "all": all,
                        "last_event_id": last_event_id,
                    },
                    session_get_events_params.SessionGetEventsParams,
                ),
            ),
            cast_to=cast(
                Any, SessionGetEventsResponse
            ),  # Union types cannot be passed in as arguments in the type system
            stream=True,
            stream_cls=Stream[SessionGetEventsResponse],
        )

    def save_profile_on_termination(
        self,
        profile_name: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Save profile on termination

        Args:
          session_id: ID of the session.

          profile_name: Name under which to save the profile.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not profile_name:
            raise ValueError(f"Expected a non-empty value for `profile_name` but received {profile_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/sessions/{session_id}/save-profile-on-termination/{profile_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def terminate(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Ends a session by ID.

        If a given session id does not exist within the
        organization, it is ignored.

        Args:
          id: ID of the session to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/sessions/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncSessionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#with_streaming_response
        """
        return AsyncSessionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        configuration: SessionConfigV1 | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SessionResponse:
        """
        Create a session

        Args:
          configuration: Session configuration

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/sessions",
            body=await async_maybe_transform(
                {"configuration": configuration}, session_create_params.SessionCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionResponse,
        )

    async def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        session_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        status: Literal["awaitingCapacity", "initializing", "running", "ended", "completed", "cancelled", "all"]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SessionsResponse:
        """
        Get a list of sessions by ID

        Args:
          limit: Limit for pagination.

          offset: Offset for pagination.

          session_ids: A comma-separated list of IDs of the sessions to retrieve.

          status: Status of the session to get.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "session_ids": session_ids,
                        "status": status,
                    },
                    session_list_params.SessionListParams,
                ),
            ),
            cast_to=SessionsResponse,
        )

    async def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SessionResponse:
        """
        Get a session by ID

        Args:
          id: Id of the session to get

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/sessions/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionResponse,
        )

    async def get_events(
        self,
        id: str,
        *,
        all: bool | NotGiven = NOT_GIVEN,
        last_event_id: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[SessionGetEventsResponse]:
        """
        Get a session event stream for a given session ID

        Args:
          id: ID of the session to get status info for

          all: Get all events

          last_event_id: last known event id

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        return await self._get(
            f"/sessions/{id}/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "all": all,
                        "last_event_id": last_event_id,
                    },
                    session_get_events_params.SessionGetEventsParams,
                ),
            ),
            cast_to=cast(
                Any, SessionGetEventsResponse
            ),  # Union types cannot be passed in as arguments in the type system
            stream=True,
            stream_cls=AsyncStream[SessionGetEventsResponse],
        )

    async def save_profile_on_termination(
        self,
        profile_name: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Save profile on termination

        Args:
          session_id: ID of the session.

          profile_name: Name under which to save the profile.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not profile_name:
            raise ValueError(f"Expected a non-empty value for `profile_name` but received {profile_name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/sessions/{session_id}/save-profile-on-termination/{profile_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def terminate(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Ends a session by ID.

        If a given session id does not exist within the
        organization, it is ignored.

        Args:
          id: ID of the session to delete.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/sessions/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class SessionsResourceWithRawResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_raw_response_wrapper(
            sessions.create,
        )
        self.list = to_raw_response_wrapper(
            sessions.list,
        )
        self.get = to_raw_response_wrapper(
            sessions.get,
        )
        self.get_events = to_raw_response_wrapper(
            sessions.get_events,
        )
        self.save_profile_on_termination = to_raw_response_wrapper(
            sessions.save_profile_on_termination,
        )
        self.terminate = to_raw_response_wrapper(
            sessions.terminate,
        )


class AsyncSessionsResourceWithRawResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_raw_response_wrapper(
            sessions.create,
        )
        self.list = async_to_raw_response_wrapper(
            sessions.list,
        )
        self.get = async_to_raw_response_wrapper(
            sessions.get,
        )
        self.get_events = async_to_raw_response_wrapper(
            sessions.get_events,
        )
        self.save_profile_on_termination = async_to_raw_response_wrapper(
            sessions.save_profile_on_termination,
        )
        self.terminate = async_to_raw_response_wrapper(
            sessions.terminate,
        )


class SessionsResourceWithStreamingResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_streamed_response_wrapper(
            sessions.create,
        )
        self.list = to_streamed_response_wrapper(
            sessions.list,
        )
        self.get = to_streamed_response_wrapper(
            sessions.get,
        )
        self.get_events = to_streamed_response_wrapper(
            sessions.get_events,
        )
        self.save_profile_on_termination = to_streamed_response_wrapper(
            sessions.save_profile_on_termination,
        )
        self.terminate = to_streamed_response_wrapper(
            sessions.terminate,
        )


class AsyncSessionsResourceWithStreamingResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_streamed_response_wrapper(
            sessions.create,
        )
        self.list = async_to_streamed_response_wrapper(
            sessions.list,
        )
        self.get = async_to_streamed_response_wrapper(
            sessions.get,
        )
        self.get_events = async_to_streamed_response_wrapper(
            sessions.get_events,
        )
        self.save_profile_on_termination = async_to_streamed_response_wrapper(
            sessions.save_profile_on_termination,
        )
        self.terminate = async_to_streamed_response_wrapper(
            sessions.terminate,
        )
