# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import (
    window_get_params,
    window_type_params,
    window_click_params,
    window_hover_params,
    window_create_params,
    window_scrape_params,
    window_scroll_params,
    window_monitor_params,
    window_load_url_params,
    window_summarize_params,
    window_page_query_params,
    window_screenshot_params,
    window_prompt_content_params,
    window_paginated_extraction_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
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
from .._base_client import make_request_options
from ..types.shared.scrape_response import ScrapeResponse
from ..types.shared.window_response import WindowResponse
from ..types.shared.ai_prompt_response import AIPromptResponse
from ..types.shared_params.click_config import ClickConfig
from ..types.shared_params.monitor_config import MonitorConfig
from ..types.shared_params.summary_config import SummaryConfig
from ..types.shared.window_id_data_response import WindowIDDataResponse
from ..types.shared_params.scroll_by_config import ScrollByConfig
from ..types.shared_params.page_query_config import PageQueryConfig
from ..types.shared.operation_outcome_response import OperationOutcomeResponse
from ..types.shared_params.scroll_to_edge_config import ScrollToEdgeConfig
from ..types.shared_params.micro_interaction_config import MicroInteractionConfig
from ..types.shared_params.screenshot_request_config import ScreenshotRequestConfig
from ..types.shared_params.paginated_extraction_config import PaginatedExtractionConfig

__all__ = ["WindowsResource", "AsyncWindowsResource"]


class WindowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WindowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#accessing-raw-response-data-eg-headers
        """
        return WindowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WindowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#with_streaming_response
        """
        return WindowsResourceWithStreamingResponse(self)

    def create(
        self,
        session_id: str,
        *,
        screen_resolution: str | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        wait_until: Literal["load", "domContentLoaded", "complete", "noWait"] | NotGiven = NOT_GIVEN,
        wait_until_timeout_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WindowIDDataResponse:
        """Creates a new browser window in a session.

        Optionally, you can specify a url to
        load on the window upon creation.

        Args:
          session_id: ID of the session that owns the window.

          screen_resolution: Affects the live view configuration. By default, a live view will fill the
              parent frame (or local window if loaded directly) when initially loaded, causing
              the browser window to be resized to match. This parameter can be used to instead
              configure the returned liveViewUrl so that the live view is loaded with fixed
              dimensions (e.g. 1280x720), resizing the browser window to match, and then
              disallows any further resizing from the live view.

          url: Initial url to navigate to

          wait_until: Wait until the specified loading event occurs. Defaults to 'load', which waits
              until the page dom and it's assets have loaded. 'domContentLoaded' will wait
              until the dom has loaded, 'complete' will wait until the page and all it's
              iframes have loaded it's dom and assets. 'noWait' will not wait for any loading
              event and will return immediately.

          wait_until_timeout_seconds: Maximum time in seconds to wait for the specified loading event to occur before
              timing out.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows",
            body=maybe_transform(
                {
                    "screen_resolution": screen_resolution,
                    "url": url,
                    "wait_until": wait_until,
                    "wait_until_timeout_seconds": wait_until_timeout_seconds,
                },
                window_create_params.WindowCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WindowIDDataResponse,
        )

    def click(
        self,
        window_id: str,
        *,
        session_id: str,
        element_description: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: ClickConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        wait_for_navigation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a click interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          element_description: A natural language description of the element to click.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          wait_for_navigation: If true, Airtop AI will wait for the navigation to complete after clicking the
              element.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/click",
            body=maybe_transform(
                {
                    "element_description": element_description,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                    "wait_for_navigation": wait_for_navigation,
                },
                window_click_params.WindowClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def close(
        self,
        window_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WindowIDDataResponse:
        """
        Closes a browser window in a session

        Args:
          session_id: ID of the session that owns the window.

          window_id: Airtop window ID of the browser window.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._delete(
            f"/sessions/{session_id}/windows/{window_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WindowIDDataResponse,
        )

    def get(
        self,
        window_id: str,
        *,
        session_id: str,
        disable_resize: bool | NotGiven = NOT_GIVEN,
        include_navigation_bar: bool | NotGiven = NOT_GIVEN,
        screen_resolution: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WindowResponse:
        """
        Get information about a browser window in a session, including the live view
        url.

        Args:
          session_id: ID of the session that owns the window.

          window_id: ID of the browser window, which can either be a normal AirTop windowId or a
              [CDP TargetId](https://chromedevtools.github.io/devtools-protocol/tot/Target/#type-TargetID)
              from a browser automation library like Puppeteer (typically associated with the
              page or main frame). Our SDKs will handle retrieving a TargetId for you from
              various popular browser automation libraries, but we also have details in our
              guides on how to do it manually.

          disable_resize: Affects the live view configuration. Set to true to configure the returned
              liveViewUrl so that the ability to resize the browser window from the live view
              is disabled (resizing is allowed by default). Note that, at initial load, the
              live view will automatically fill the parent frame (or local window if loaded
              directly) and cause the browser window to be resized to match. This parameter
              does not affect that initial load behavior. See screenResolution for a way to
              set a fixed size for the live view.

          include_navigation_bar: Affects the live view configuration. A navigation bar is not shown in the live
              view of a browser by default. Set this to true to configure the returned
              liveViewUrl so that a navigation bar is rendered, allowing users to easily
              navigate the browser to other pages from the live view.

          screen_resolution: Affects the live view configuration. By default, a live view will fill the
              parent frame (or local window if loaded directly) when initially loaded, causing
              the browser window to be resized to match. This parameter can be used to instead
              configure the returned liveViewUrl so that the live view is loaded with fixed
              dimensions (e.g. 1280x720), resizing the browser window to match, and then
              disallows any further resizing from the live view.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._get(
            f"/sessions/{session_id}/windows/{window_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "disable_resize": disable_resize,
                        "include_navigation_bar": include_navigation_bar,
                        "screen_resolution": screen_resolution,
                    },
                    window_get_params.WindowGetParams,
                ),
            ),
            cast_to=WindowResponse,
        )

    def hover(
        self,
        window_id: str,
        *,
        session_id: str,
        element_description: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: window_hover_params.Configuration | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a hover interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          element_description: A natural language description of where to hover (e.g. 'the search box',
              'username field'). The interaction will be aborted if the target element cannot
              be found.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/hover",
            body=maybe_transform(
                {
                    "element_description": element_description,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_hover_params.WindowHoverParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def load_url(
        self,
        window_id: str,
        *,
        session_id: str,
        url: str,
        wait_until: Literal["load", "domContentLoaded", "complete", "noWait"] | NotGiven = NOT_GIVEN,
        wait_until_timeout_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OperationOutcomeResponse:
        """
        Loads a specified url on a given window

        Args:
          session_id: ID of the session that owns the window.

          window_id: Airtop window ID of the browser window.

          url: Url to navigate to

          wait_until: Wait until the specified loading event occurs. Defaults to 'load', which waits
              until the page dom and it's assets have loaded. 'domContentLoaded' will wait
              until the dom has loaded, 'complete' will wait until the page and all it's
              iframes have loaded it's dom and assets. 'noWait' will not wait for any loading
              event and will return immediately.

          wait_until_timeout_seconds: Maximum time in seconds to wait for the specified loading event to occur before
              timing out.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}",
            body=maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                    "wait_until_timeout_seconds": wait_until_timeout_seconds,
                },
                window_load_url_params.WindowLoadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OperationOutcomeResponse,
        )

    def monitor(
        self,
        window_id: str,
        *,
        session_id: str,
        condition: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: MonitorConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Monitor for a condition

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          condition: A natural language description of the condition to monitor for in the browser
              window.

          configuration: Monitor configuration. If not specified, defaults to an interval monitor with a
              5 second interval.

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/monitor",
            body=maybe_transform(
                {
                    "condition": condition,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_monitor_params.WindowMonitorParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def page_query(
        self,
        window_id: str,
        *,
        session_id: str,
        prompt: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: PageQueryConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        follow_pagination_links: bool | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """Submit a prompt that queries the content of a specific browser window.

        You may
        extract content from the page, or ask a question about the page and allow the AI
        to answer it (ex. Is the user logged in?).

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          prompt: The prompt to submit about the content in the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          follow_pagination_links: Make a best effort attempt to load more content items than are originally
              displayed on the page, e.g. by following pagination links, clicking controls to
              load more content, utilizing infinite scrolling, etc. This can be quite a bit
              more costly, but may be necessary for sites that require additional interaction
              to show the needed results. You can provide constraints in your prompt (e.g. on
              the total number of pages or results to consider).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/page-query",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "follow_pagination_links": follow_pagination_links,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_page_query_params.WindowPageQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def paginated_extraction(
        self,
        window_id: str,
        *,
        session_id: str,
        prompt: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: PaginatedExtractionConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Submit a prompt that queries the content of a specific browser window and
        paginates through pages to return a list of results.

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          prompt: A prompt providing the Airtop AI model with additional direction or constraints
              about the page and the details you want to extract from the page.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/paginated-extraction",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_paginated_extraction_params.WindowPaginatedExtractionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def prompt_content(
        self,
        window_id: str,
        *,
        session_id: str,
        prompt: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: PageQueryConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        follow_pagination_links: bool | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """This endpoint is deprecated.

        Please use the `pageQuery` endpoint instead.

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          prompt: The prompt to submit about the content in the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          follow_pagination_links: Make a best effort attempt to load more content items than are originally
              displayed on the page, e.g. by following pagination links, clicking controls to
              load more content, utilizing infinite scrolling, etc. This can be quite a bit
              more costly, but may be necessary for sites that require additional interaction
              to show the needed results. You can provide constraints in your prompt (e.g. on
              the total number of pages or results to consider).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/prompt-content",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "follow_pagination_links": follow_pagination_links,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_prompt_content_params.WindowPromptContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def scrape(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeResponse:
        """
        Scrape a window and return the content as markdown

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window to scrape.

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/scrape-content",
            body=maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_scrape_params.WindowScrapeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeResponse,
        )

    def screenshot(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: ScreenshotRequestConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Take a screenshot of a browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/screenshot",
            body=maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_screenshot_params.WindowScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def scroll(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: MicroInteractionConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        scroll_by: ScrollByConfig | NotGiven = NOT_GIVEN,
        scroll_to_edge: ScrollToEdgeConfig | NotGiven = NOT_GIVEN,
        scroll_to_element: str | NotGiven = NOT_GIVEN,
        scroll_within: str | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a scroll interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          scroll_by: The amount of pixels/percentage to scroll horizontally or vertically relative to
              the current scroll position. Positive values scroll right and down, negative
              values scroll left and up. If a scrollToElement value is provided,
              scrollBy/scrollToEdge values will be ignored.

          scroll_to_edge: Scroll to the top or bottom of the page, or to the left or right of the page.
              ScrollToEdge values will take precedence over the scrollBy values, and
              scrollToEdge will be executed first. If a scrollToElement value is provided,
              scrollToEdge/scrollBy values will be ignored.

          scroll_to_element: A natural language description of where to scroll (e.g. 'the search box',
              'username field'). The interaction will be aborted if the target element cannot
              be found. If provided, scrollToEdge/scrollBy values will be ignored.

          scroll_within: A natural language description of the scrollable area on the web page. This
              identifies the container or region that should be scrolled. If missing, the
              entire page will be scrolled. You can also describe a visible reference point
              inside the container. Note: This is different from scrollToElement, which
              specifies the target element to scroll to. The target may be located inside the
              scrollable area defined by scrollWithin.

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/scroll",
            body=maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "scroll_by": scroll_by,
                    "scroll_to_edge": scroll_to_edge,
                    "scroll_to_element": scroll_to_element,
                    "scroll_within": scroll_within,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_scroll_params.WindowScrollParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def summarize(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: SummaryConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """This endpoint is deprecated.

        Please use the `pageQuery` endpoint and ask for a
        summary in the prompt instead.

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window to summarize.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          prompt: An optional prompt providing the Airtop AI model with additional direction or
              constraints about the summary (such as desired length).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/summarize-content",
            body=maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "prompt": prompt,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_summarize_params.WindowSummarizeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    def type(
        self,
        window_id: str,
        *,
        session_id: str,
        text: str,
        clear_input_field: bool | NotGiven = NOT_GIVEN,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: window_type_params.Configuration | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        element_description: str | NotGiven = NOT_GIVEN,
        press_enter_key: bool | NotGiven = NOT_GIVEN,
        press_tab_key: bool | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        wait_for_navigation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a type interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          text: The text to type into the browser window.

          clear_input_field: If true, and an HTML input field is active, clears the input field before typing
              the text.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          element_description: A natural language description of where to type (e.g. 'the search box',
              'username field'). The interaction will be aborted if the target element cannot
              be found.

          press_enter_key: If true, simulates pressing the Enter key after typing the text.

          press_tab_key: If true, simulates pressing the Tab key after typing the text. Note that the tab
              key will be pressed after the Enter key if both options are configured.

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          wait_for_navigation: If true, Airtop AI will wait for the navigation to complete after clicking the
              element.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return self._post(
            f"/sessions/{session_id}/windows/{window_id}/type",
            body=maybe_transform(
                {
                    "text": text,
                    "clear_input_field": clear_input_field,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "element_description": element_description,
                    "press_enter_key": press_enter_key,
                    "press_tab_key": press_tab_key,
                    "time_threshold_seconds": time_threshold_seconds,
                    "wait_for_navigation": wait_for_navigation,
                },
                window_type_params.WindowTypeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )


class AsyncWindowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWindowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWindowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWindowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/airtop-ai/airtop-core-sdk-python#with_streaming_response
        """
        return AsyncWindowsResourceWithStreamingResponse(self)

    async def create(
        self,
        session_id: str,
        *,
        screen_resolution: str | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        wait_until: Literal["load", "domContentLoaded", "complete", "noWait"] | NotGiven = NOT_GIVEN,
        wait_until_timeout_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WindowIDDataResponse:
        """Creates a new browser window in a session.

        Optionally, you can specify a url to
        load on the window upon creation.

        Args:
          session_id: ID of the session that owns the window.

          screen_resolution: Affects the live view configuration. By default, a live view will fill the
              parent frame (or local window if loaded directly) when initially loaded, causing
              the browser window to be resized to match. This parameter can be used to instead
              configure the returned liveViewUrl so that the live view is loaded with fixed
              dimensions (e.g. 1280x720), resizing the browser window to match, and then
              disallows any further resizing from the live view.

          url: Initial url to navigate to

          wait_until: Wait until the specified loading event occurs. Defaults to 'load', which waits
              until the page dom and it's assets have loaded. 'domContentLoaded' will wait
              until the dom has loaded, 'complete' will wait until the page and all it's
              iframes have loaded it's dom and assets. 'noWait' will not wait for any loading
              event and will return immediately.

          wait_until_timeout_seconds: Maximum time in seconds to wait for the specified loading event to occur before
              timing out.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows",
            body=await async_maybe_transform(
                {
                    "screen_resolution": screen_resolution,
                    "url": url,
                    "wait_until": wait_until,
                    "wait_until_timeout_seconds": wait_until_timeout_seconds,
                },
                window_create_params.WindowCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WindowIDDataResponse,
        )

    async def click(
        self,
        window_id: str,
        *,
        session_id: str,
        element_description: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: ClickConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        wait_for_navigation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a click interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          element_description: A natural language description of the element to click.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          wait_for_navigation: If true, Airtop AI will wait for the navigation to complete after clicking the
              element.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/click",
            body=await async_maybe_transform(
                {
                    "element_description": element_description,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                    "wait_for_navigation": wait_for_navigation,
                },
                window_click_params.WindowClickParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def close(
        self,
        window_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WindowIDDataResponse:
        """
        Closes a browser window in a session

        Args:
          session_id: ID of the session that owns the window.

          window_id: Airtop window ID of the browser window.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._delete(
            f"/sessions/{session_id}/windows/{window_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WindowIDDataResponse,
        )

    async def get(
        self,
        window_id: str,
        *,
        session_id: str,
        disable_resize: bool | NotGiven = NOT_GIVEN,
        include_navigation_bar: bool | NotGiven = NOT_GIVEN,
        screen_resolution: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WindowResponse:
        """
        Get information about a browser window in a session, including the live view
        url.

        Args:
          session_id: ID of the session that owns the window.

          window_id: ID of the browser window, which can either be a normal AirTop windowId or a
              [CDP TargetId](https://chromedevtools.github.io/devtools-protocol/tot/Target/#type-TargetID)
              from a browser automation library like Puppeteer (typically associated with the
              page or main frame). Our SDKs will handle retrieving a TargetId for you from
              various popular browser automation libraries, but we also have details in our
              guides on how to do it manually.

          disable_resize: Affects the live view configuration. Set to true to configure the returned
              liveViewUrl so that the ability to resize the browser window from the live view
              is disabled (resizing is allowed by default). Note that, at initial load, the
              live view will automatically fill the parent frame (or local window if loaded
              directly) and cause the browser window to be resized to match. This parameter
              does not affect that initial load behavior. See screenResolution for a way to
              set a fixed size for the live view.

          include_navigation_bar: Affects the live view configuration. A navigation bar is not shown in the live
              view of a browser by default. Set this to true to configure the returned
              liveViewUrl so that a navigation bar is rendered, allowing users to easily
              navigate the browser to other pages from the live view.

          screen_resolution: Affects the live view configuration. By default, a live view will fill the
              parent frame (or local window if loaded directly) when initially loaded, causing
              the browser window to be resized to match. This parameter can be used to instead
              configure the returned liveViewUrl so that the live view is loaded with fixed
              dimensions (e.g. 1280x720), resizing the browser window to match, and then
              disallows any further resizing from the live view.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._get(
            f"/sessions/{session_id}/windows/{window_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "disable_resize": disable_resize,
                        "include_navigation_bar": include_navigation_bar,
                        "screen_resolution": screen_resolution,
                    },
                    window_get_params.WindowGetParams,
                ),
            ),
            cast_to=WindowResponse,
        )

    async def hover(
        self,
        window_id: str,
        *,
        session_id: str,
        element_description: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: window_hover_params.Configuration | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a hover interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          element_description: A natural language description of where to hover (e.g. 'the search box',
              'username field'). The interaction will be aborted if the target element cannot
              be found.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/hover",
            body=await async_maybe_transform(
                {
                    "element_description": element_description,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_hover_params.WindowHoverParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def load_url(
        self,
        window_id: str,
        *,
        session_id: str,
        url: str,
        wait_until: Literal["load", "domContentLoaded", "complete", "noWait"] | NotGiven = NOT_GIVEN,
        wait_until_timeout_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OperationOutcomeResponse:
        """
        Loads a specified url on a given window

        Args:
          session_id: ID of the session that owns the window.

          window_id: Airtop window ID of the browser window.

          url: Url to navigate to

          wait_until: Wait until the specified loading event occurs. Defaults to 'load', which waits
              until the page dom and it's assets have loaded. 'domContentLoaded' will wait
              until the dom has loaded, 'complete' will wait until the page and all it's
              iframes have loaded it's dom and assets. 'noWait' will not wait for any loading
              event and will return immediately.

          wait_until_timeout_seconds: Maximum time in seconds to wait for the specified loading event to occur before
              timing out.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "wait_until": wait_until,
                    "wait_until_timeout_seconds": wait_until_timeout_seconds,
                },
                window_load_url_params.WindowLoadURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OperationOutcomeResponse,
        )

    async def monitor(
        self,
        window_id: str,
        *,
        session_id: str,
        condition: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: MonitorConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Monitor for a condition

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          condition: A natural language description of the condition to monitor for in the browser
              window.

          configuration: Monitor configuration. If not specified, defaults to an interval monitor with a
              5 second interval.

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/monitor",
            body=await async_maybe_transform(
                {
                    "condition": condition,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_monitor_params.WindowMonitorParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def page_query(
        self,
        window_id: str,
        *,
        session_id: str,
        prompt: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: PageQueryConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        follow_pagination_links: bool | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """Submit a prompt that queries the content of a specific browser window.

        You may
        extract content from the page, or ask a question about the page and allow the AI
        to answer it (ex. Is the user logged in?).

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          prompt: The prompt to submit about the content in the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          follow_pagination_links: Make a best effort attempt to load more content items than are originally
              displayed on the page, e.g. by following pagination links, clicking controls to
              load more content, utilizing infinite scrolling, etc. This can be quite a bit
              more costly, but may be necessary for sites that require additional interaction
              to show the needed results. You can provide constraints in your prompt (e.g. on
              the total number of pages or results to consider).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/page-query",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "follow_pagination_links": follow_pagination_links,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_page_query_params.WindowPageQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def paginated_extraction(
        self,
        window_id: str,
        *,
        session_id: str,
        prompt: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: PaginatedExtractionConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Submit a prompt that queries the content of a specific browser window and
        paginates through pages to return a list of results.

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          prompt: A prompt providing the Airtop AI model with additional direction or constraints
              about the page and the details you want to extract from the page.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/paginated-extraction",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_paginated_extraction_params.WindowPaginatedExtractionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def prompt_content(
        self,
        window_id: str,
        *,
        session_id: str,
        prompt: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: PageQueryConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        follow_pagination_links: bool | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """This endpoint is deprecated.

        Please use the `pageQuery` endpoint instead.

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          prompt: The prompt to submit about the content in the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          follow_pagination_links: Make a best effort attempt to load more content items than are originally
              displayed on the page, e.g. by following pagination links, clicking controls to
              load more content, utilizing infinite scrolling, etc. This can be quite a bit
              more costly, but may be necessary for sites that require additional interaction
              to show the needed results. You can provide constraints in your prompt (e.g. on
              the total number of pages or results to consider).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/prompt-content",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "follow_pagination_links": follow_pagination_links,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_prompt_content_params.WindowPromptContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def scrape(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ScrapeResponse:
        """
        Scrape a window and return the content as markdown

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window to scrape.

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/scrape-content",
            body=await async_maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_scrape_params.WindowScrapeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ScrapeResponse,
        )

    async def screenshot(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: ScreenshotRequestConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Take a screenshot of a browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/screenshot",
            body=await async_maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_screenshot_params.WindowScreenshotParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def scroll(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: MicroInteractionConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        scroll_by: ScrollByConfig | NotGiven = NOT_GIVEN,
        scroll_to_edge: ScrollToEdgeConfig | NotGiven = NOT_GIVEN,
        scroll_to_element: str | NotGiven = NOT_GIVEN,
        scroll_within: str | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a scroll interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          scroll_by: The amount of pixels/percentage to scroll horizontally or vertically relative to
              the current scroll position. Positive values scroll right and down, negative
              values scroll left and up. If a scrollToElement value is provided,
              scrollBy/scrollToEdge values will be ignored.

          scroll_to_edge: Scroll to the top or bottom of the page, or to the left or right of the page.
              ScrollToEdge values will take precedence over the scrollBy values, and
              scrollToEdge will be executed first. If a scrollToElement value is provided,
              scrollToEdge/scrollBy values will be ignored.

          scroll_to_element: A natural language description of where to scroll (e.g. 'the search box',
              'username field'). The interaction will be aborted if the target element cannot
              be found. If provided, scrollToEdge/scrollBy values will be ignored.

          scroll_within: A natural language description of the scrollable area on the web page. This
              identifies the container or region that should be scrolled. If missing, the
              entire page will be scrolled. You can also describe a visible reference point
              inside the container. Note: This is different from scrollToElement, which
              specifies the target element to scroll to. The target may be located inside the
              scrollable area defined by scrollWithin.

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/scroll",
            body=await async_maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "scroll_by": scroll_by,
                    "scroll_to_edge": scroll_to_edge,
                    "scroll_to_element": scroll_to_element,
                    "scroll_within": scroll_within,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_scroll_params.WindowScrollParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def summarize(
        self,
        window_id: str,
        *,
        session_id: str,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: SummaryConfig | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """This endpoint is deprecated.

        Please use the `pageQuery` endpoint and ask for a
        summary in the prompt instead.

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window to summarize.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          prompt: An optional prompt providing the Airtop AI model with additional direction or
              constraints about the summary (such as desired length).

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/summarize-content",
            body=await async_maybe_transform(
                {
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "prompt": prompt,
                    "time_threshold_seconds": time_threshold_seconds,
                },
                window_summarize_params.WindowSummarizeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )

    async def type(
        self,
        window_id: str,
        *,
        session_id: str,
        text: str,
        clear_input_field: bool | NotGiven = NOT_GIVEN,
        client_request_id: str | NotGiven = NOT_GIVEN,
        configuration: window_type_params.Configuration | NotGiven = NOT_GIVEN,
        cost_threshold_credits: int | NotGiven = NOT_GIVEN,
        element_description: str | NotGiven = NOT_GIVEN,
        press_enter_key: bool | NotGiven = NOT_GIVEN,
        press_tab_key: bool | NotGiven = NOT_GIVEN,
        time_threshold_seconds: int | NotGiven = NOT_GIVEN,
        wait_for_navigation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIPromptResponse:
        """
        Execute a type interaction in a specific browser window

        Args:
          session_id: The session id for the window.

          window_id: The Airtop window id of the browser window.

          text: The text to type into the browser window.

          clear_input_field: If true, and an HTML input field is active, clears the input field before typing
              the text.

          configuration: Request configuration

          cost_threshold_credits: A credit threshold that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

          element_description: A natural language description of where to type (e.g. 'the search box',
              'username field'). The interaction will be aborted if the target element cannot
              be found.

          press_enter_key: If true, simulates pressing the Enter key after typing the text.

          press_tab_key: If true, simulates pressing the Tab key after typing the text. Note that the tab
              key will be pressed after the Enter key if both options are configured.

          time_threshold_seconds: A time threshold in seconds that, once exceeded, will cause the operation to be
              cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
              periodically during the course of fulfilling the request. A default threshold is
              used if not specified, but you can use this option to increase or decrease as
              needed. Set to 0 to disable this feature entirely (not recommended).

              This setting does not extend the maximum session duration provided at the time
              of session creation.

          wait_for_navigation: If true, Airtop AI will wait for the navigation to complete after clicking the
              element.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not window_id:
            raise ValueError(f"Expected a non-empty value for `window_id` but received {window_id!r}")
        return await self._post(
            f"/sessions/{session_id}/windows/{window_id}/type",
            body=await async_maybe_transform(
                {
                    "text": text,
                    "clear_input_field": clear_input_field,
                    "client_request_id": client_request_id,
                    "configuration": configuration,
                    "cost_threshold_credits": cost_threshold_credits,
                    "element_description": element_description,
                    "press_enter_key": press_enter_key,
                    "press_tab_key": press_tab_key,
                    "time_threshold_seconds": time_threshold_seconds,
                    "wait_for_navigation": wait_for_navigation,
                },
                window_type_params.WindowTypeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIPromptResponse,
        )


class WindowsResourceWithRawResponse:
    def __init__(self, windows: WindowsResource) -> None:
        self._windows = windows

        self.create = to_raw_response_wrapper(
            windows.create,
        )
        self.click = to_raw_response_wrapper(
            windows.click,
        )
        self.close = to_raw_response_wrapper(
            windows.close,
        )
        self.get = to_raw_response_wrapper(
            windows.get,
        )
        self.hover = to_raw_response_wrapper(
            windows.hover,
        )
        self.load_url = to_raw_response_wrapper(
            windows.load_url,
        )
        self.monitor = to_raw_response_wrapper(
            windows.monitor,
        )
        self.page_query = to_raw_response_wrapper(
            windows.page_query,
        )
        self.paginated_extraction = to_raw_response_wrapper(
            windows.paginated_extraction,
        )
        self.prompt_content = to_raw_response_wrapper(
            windows.prompt_content,
        )
        self.scrape = to_raw_response_wrapper(
            windows.scrape,
        )
        self.screenshot = to_raw_response_wrapper(
            windows.screenshot,
        )
        self.scroll = to_raw_response_wrapper(
            windows.scroll,
        )
        self.summarize = to_raw_response_wrapper(
            windows.summarize,
        )
        self.type = to_raw_response_wrapper(
            windows.type,
        )


class AsyncWindowsResourceWithRawResponse:
    def __init__(self, windows: AsyncWindowsResource) -> None:
        self._windows = windows

        self.create = async_to_raw_response_wrapper(
            windows.create,
        )
        self.click = async_to_raw_response_wrapper(
            windows.click,
        )
        self.close = async_to_raw_response_wrapper(
            windows.close,
        )
        self.get = async_to_raw_response_wrapper(
            windows.get,
        )
        self.hover = async_to_raw_response_wrapper(
            windows.hover,
        )
        self.load_url = async_to_raw_response_wrapper(
            windows.load_url,
        )
        self.monitor = async_to_raw_response_wrapper(
            windows.monitor,
        )
        self.page_query = async_to_raw_response_wrapper(
            windows.page_query,
        )
        self.paginated_extraction = async_to_raw_response_wrapper(
            windows.paginated_extraction,
        )
        self.prompt_content = async_to_raw_response_wrapper(
            windows.prompt_content,
        )
        self.scrape = async_to_raw_response_wrapper(
            windows.scrape,
        )
        self.screenshot = async_to_raw_response_wrapper(
            windows.screenshot,
        )
        self.scroll = async_to_raw_response_wrapper(
            windows.scroll,
        )
        self.summarize = async_to_raw_response_wrapper(
            windows.summarize,
        )
        self.type = async_to_raw_response_wrapper(
            windows.type,
        )


class WindowsResourceWithStreamingResponse:
    def __init__(self, windows: WindowsResource) -> None:
        self._windows = windows

        self.create = to_streamed_response_wrapper(
            windows.create,
        )
        self.click = to_streamed_response_wrapper(
            windows.click,
        )
        self.close = to_streamed_response_wrapper(
            windows.close,
        )
        self.get = to_streamed_response_wrapper(
            windows.get,
        )
        self.hover = to_streamed_response_wrapper(
            windows.hover,
        )
        self.load_url = to_streamed_response_wrapper(
            windows.load_url,
        )
        self.monitor = to_streamed_response_wrapper(
            windows.monitor,
        )
        self.page_query = to_streamed_response_wrapper(
            windows.page_query,
        )
        self.paginated_extraction = to_streamed_response_wrapper(
            windows.paginated_extraction,
        )
        self.prompt_content = to_streamed_response_wrapper(
            windows.prompt_content,
        )
        self.scrape = to_streamed_response_wrapper(
            windows.scrape,
        )
        self.screenshot = to_streamed_response_wrapper(
            windows.screenshot,
        )
        self.scroll = to_streamed_response_wrapper(
            windows.scroll,
        )
        self.summarize = to_streamed_response_wrapper(
            windows.summarize,
        )
        self.type = to_streamed_response_wrapper(
            windows.type,
        )


class AsyncWindowsResourceWithStreamingResponse:
    def __init__(self, windows: AsyncWindowsResource) -> None:
        self._windows = windows

        self.create = async_to_streamed_response_wrapper(
            windows.create,
        )
        self.click = async_to_streamed_response_wrapper(
            windows.click,
        )
        self.close = async_to_streamed_response_wrapper(
            windows.close,
        )
        self.get = async_to_streamed_response_wrapper(
            windows.get,
        )
        self.hover = async_to_streamed_response_wrapper(
            windows.hover,
        )
        self.load_url = async_to_streamed_response_wrapper(
            windows.load_url,
        )
        self.monitor = async_to_streamed_response_wrapper(
            windows.monitor,
        )
        self.page_query = async_to_streamed_response_wrapper(
            windows.page_query,
        )
        self.paginated_extraction = async_to_streamed_response_wrapper(
            windows.paginated_extraction,
        )
        self.prompt_content = async_to_streamed_response_wrapper(
            windows.prompt_content,
        )
        self.scrape = async_to_streamed_response_wrapper(
            windows.scrape,
        )
        self.screenshot = async_to_streamed_response_wrapper(
            windows.screenshot,
        )
        self.scroll = async_to_streamed_response_wrapper(
            windows.scroll,
        )
        self.summarize = async_to_streamed_response_wrapper(
            windows.summarize,
        )
        self.type = async_to_streamed_response_wrapper(
            windows.type,
        )
