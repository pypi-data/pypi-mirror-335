# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .shared import (
    Issue as Issue,
    ErrorBody as ErrorBody,
    ErrorModel as ErrorModel,
    WindowInfo as WindowInfo,
    AsyncConfig as AsyncConfig,
    ClickConfig as ClickConfig,
    ErrorDetail as ErrorDetail,
    GetFileData as GetFileData,
    ErrorMessage as ErrorMessage,
    ScrapeConfig as ScrapeConfig,
    WindowIDData as WindowIDData,
    MonitorConfig as MonitorConfig,
    ProfileOutput as ProfileOutput,
    StatusMessage as StatusMessage,
    SummaryConfig as SummaryConfig,
    AutomationData as AutomationData,
    CreateFileData as CreateFileData,
    ScrapeResponse as ScrapeResponse,
    ScrollByConfig as ScrollByConfig,
    WindowResponse as WindowResponse,
    GetFileResponse as GetFileResponse,
    PageQueryConfig as PageQueryConfig,
    SessionConfigV1 as SessionConfigV1,
    SessionResponse as SessionResponse,
    AIPromptResponse as AIPromptResponse,
    AirtopPagination as AirtopPagination,
    AsyncTypeRequest as AsyncTypeRequest,
    OperationOutcome as OperationOutcome,
    ScreenshotConfig as ScreenshotConfig,
    SessionsResponse as SessionsResponse,
    AsyncClickRequest as AsyncClickRequest,
    AsyncHoverRequest as AsyncHoverRequest,
    CreateFileRequest as CreateFileRequest,
    AIResponseEnvelope as AIResponseEnvelope,
    CreateFileResponse as CreateFileResponse,
    ScreenshotMetadata as ScreenshotMetadata,
    ScrollToEdgeConfig as ScrollToEdgeConfig,
    SessionRestInputV1 as SessionRestInputV1,
    WindowEventMessage as WindowEventMessage,
    AsyncMonitorRequest as AsyncMonitorRequest,
    EnvelopeDefaultMeta as EnvelopeDefaultMeta,
    SessionEventMessage as SessionEventMessage,
    WindowLoadURLV1Body as WindowLoadURLV1Body,
    PageQueryHandlerBody as PageQueryHandlerBody,
    ProfileRenameRequest as ProfileRenameRequest,
    ScrapeContentRequest as ScrapeContentRequest,
    ScrapeResponseOutput as ScrapeResponseOutput,
    VisualAnalysisConfig as VisualAnalysisConfig,
    WindowIDDataResponse as WindowIDDataResponse,
    AsyncPageQueryRequest as AsyncPageQueryRequest,
    ExternalSessionConfig as ExternalSessionConfig,
    IntervalMonitorConfig as IntervalMonitorConfig,
    ListAutomationsOutput as ListAutomationsOutput,
    RequestStatusResponse as RequestStatusResponse,
    ScrapeResponseContent as ScrapeResponseContent,
    AsyncScreenshotRequest as AsyncScreenshotRequest,
    MicroInteractionConfig as MicroInteractionConfig,
    ScrapeResponseEnvelope as ScrapeResponseEnvelope,
    SessionsWithPagination as SessionsWithPagination,
    CreateAutomationRequest as CreateAutomationRequest,
    CreateWindowInputV1Body as CreateWindowInputV1Body,
    ScreenshotRequestConfig as ScreenshotRequestConfig,
    DeleteAutomationResponse as DeleteAutomationResponse,
    OperationOutcomeResponse as OperationOutcomeResponse,
    AsyncPromptContentRequest as AsyncPromptContentRequest,
    PaginatedExtractionConfig as PaginatedExtractionConfig,
    SummaryExperimentalConfig as SummaryExperimentalConfig,
    BrowserWaitNavigationConfig as BrowserWaitNavigationConfig,
    PageQueryExperimentalConfig as PageQueryExperimentalConfig,
    AsyncCreateAutomationRequest as AsyncCreateAutomationRequest,
    AsyncSummarizeContentRequest as AsyncSummarizeContentRequest,
    AsyncExecuteAutomationRequest as AsyncExecuteAutomationRequest,
    SessionTypeHandlerRequestBody as SessionTypeHandlerRequestBody,
    AsyncSessionAIResponseEnvelope as AsyncSessionAIResponseEnvelope,
    ClientProvidedResponseMetadata as ClientProvidedResponseMetadata,
    SessionClickHandlerRequestBody as SessionClickHandlerRequestBody,
    SessionHoverHandlerRequestBody as SessionHoverHandlerRequestBody,
    AsyncPaginatedExtractionRequest as AsyncPaginatedExtractionRequest,
    SessionScrollHandlerRequestBody as SessionScrollHandlerRequestBody,
    SessionMonitorHandlerRequestBody as SessionMonitorHandlerRequestBody,
    SessionSummaryHandlerRequestBody as SessionSummaryHandlerRequestBody,
    ExternalSessionAIResponseMetadata as ExternalSessionAIResponseMetadata,
    ExternalSessionWithConnectionInfo as ExternalSessionWithConnectionInfo,
    UpdateAutomationDescriptionRequest as UpdateAutomationDescriptionRequest,
    SessionScreenshotHandlerRequestBody as SessionScreenshotHandlerRequestBody,
    ExternalSessionAIResponseMetadataUsage as ExternalSessionAIResponseMetadataUsage,
    SessionPaginatedExtractionHandlerRequestBody as SessionPaginatedExtractionHandlerRequestBody,
)
from .window_get_params import WindowGetParams as WindowGetParams
from .window_type_params import WindowTypeParams as WindowTypeParams
from .session_list_params import SessionListParams as SessionListParams
from .window_click_params import WindowClickParams as WindowClickParams
from .window_hover_params import WindowHoverParams as WindowHoverParams
from .window_create_params import WindowCreateParams as WindowCreateParams
from .window_scrape_params import WindowScrapeParams as WindowScrapeParams
from .window_scroll_params import WindowScrollParams as WindowScrollParams
from .profile_delete_params import ProfileDeleteParams as ProfileDeleteParams
from .profile_rename_params import ProfileRenameParams as ProfileRenameParams
from .session_create_params import SessionCreateParams as SessionCreateParams
from .window_monitor_params import WindowMonitorParams as WindowMonitorParams
from .window_load_url_params import WindowLoadURLParams as WindowLoadURLParams
from .file_create_file_params import FileCreateFileParams as FileCreateFileParams
from .window_summarize_params import WindowSummarizeParams as WindowSummarizeParams
from .window_page_query_params import WindowPageQueryParams as WindowPageQueryParams
from .window_screenshot_params import WindowScreenshotParams as WindowScreenshotParams
from .session_get_events_params import SessionGetEventsParams as SessionGetEventsParams
from .session_get_events_response import SessionGetEventsResponse as SessionGetEventsResponse
from .window_prompt_content_params import WindowPromptContentParams as WindowPromptContentParams
from .window_paginated_extraction_params import WindowPaginatedExtractionParams as WindowPaginatedExtractionParams
from .automation_update_description_params import AutomationUpdateDescriptionParams as AutomationUpdateDescriptionParams
