# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.shared.request_status_response import RequestStatusResponse

__all__ = ["RequestsResource", "AsyncRequestsResource"]


class RequestsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#accessing-raw-response-data-eg-headers
        """
        return RequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#with_streaming_response
        """
        return RequestsResourceWithStreamingResponse(self)

    def get_request_status(
        self,
        request_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RequestStatusResponse:
        """
        Get the status of an asynchronous request

        Args:
          request_id: The ID of the request to check.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not request_id:
            raise ValueError(f"Expected a non-empty value for `request_id` but received {request_id!r}")
        return self._get(
            f"/requests/{request_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RequestStatusResponse,
        )


class AsyncRequestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#with_streaming_response
        """
        return AsyncRequestsResourceWithStreamingResponse(self)

    async def get_request_status(
        self,
        request_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RequestStatusResponse:
        """
        Get the status of an asynchronous request

        Args:
          request_id: The ID of the request to check.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not request_id:
            raise ValueError(f"Expected a non-empty value for `request_id` but received {request_id!r}")
        return await self._get(
            f"/requests/{request_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RequestStatusResponse,
        )


class RequestsResourceWithRawResponse:
    def __init__(self, requests: RequestsResource) -> None:
        self._requests = requests

        self.get_request_status = to_raw_response_wrapper(
            requests.get_request_status,
        )


class AsyncRequestsResourceWithRawResponse:
    def __init__(self, requests: AsyncRequestsResource) -> None:
        self._requests = requests

        self.get_request_status = async_to_raw_response_wrapper(
            requests.get_request_status,
        )


class RequestsResourceWithStreamingResponse:
    def __init__(self, requests: RequestsResource) -> None:
        self._requests = requests

        self.get_request_status = to_streamed_response_wrapper(
            requests.get_request_status,
        )


class AsyncRequestsResourceWithStreamingResponse:
    def __init__(self, requests: AsyncRequestsResource) -> None:
        self._requests = requests

        self.get_request_status = async_to_streamed_response_wrapper(
            requests.get_request_status,
        )
