# Shared Types

```python
from airtop_core.types import (
    AIPromptResponse,
    AIResponseEnvelope,
    AirtopPagination,
    AsyncClickRequest,
    AsyncConfig,
    AsyncCreateAutomationRequest,
    AsyncExecuteAutomationRequest,
    AsyncHoverRequest,
    AsyncMonitorRequest,
    AsyncPageQueryRequest,
    AsyncPaginatedExtractionRequest,
    AsyncPromptContentRequest,
    AsyncScreenshotRequest,
    AsyncSessionAIResponseEnvelope,
    AsyncSummarizeContentRequest,
    AsyncTypeRequest,
    AutomationData,
    BrowserWaitNavigationConfig,
    ClickConfig,
    ClientProvidedResponseMetadata,
    CreateAutomationRequest,
    CreateFileData,
    CreateFileRequest,
    CreateFileResponse,
    CreateWindowInputV1Body,
    DeleteAutomationResponse,
    EnvelopeDefaultMeta,
    ErrorBody,
    ErrorDetail,
    ErrorMessage,
    ErrorModel,
    ExternalSessionAIResponseMetadata,
    ExternalSessionAIResponseMetadataUsage,
    ExternalSessionConfig,
    ExternalSessionWithConnectionInfo,
    GetFileData,
    GetFileResponse,
    IntervalMonitorConfig,
    Issue,
    ListAutomationsOutput,
    MicroInteractionConfig,
    MonitorConfig,
    OperationOutcome,
    OperationOutcomeResponse,
    PageQueryConfig,
    PageQueryExperimentalConfig,
    PageQueryHandlerBody,
    PaginatedExtractionConfig,
    ProfileOutput,
    ProfileRenameRequest,
    RequestStatusResponse,
    ScrapeConfig,
    ScrapeContentRequest,
    ScrapeResponse,
    ScrapeResponseContent,
    ScrapeResponseEnvelope,
    ScrapeResponseOutput,
    ScreenshotConfig,
    ScreenshotMetadata,
    ScreenshotRequestConfig,
    ScrollByConfig,
    ScrollToEdgeConfig,
    SessionClickHandlerRequestBody,
    SessionConfigV1,
    SessionEventMessage,
    SessionHoverHandlerRequestBody,
    SessionMonitorHandlerRequestBody,
    SessionPaginatedExtractionHandlerRequestBody,
    SessionResponse,
    SessionRestInputV1,
    SessionScreenshotHandlerRequestBody,
    SessionScrollHandlerRequestBody,
    SessionSummaryHandlerRequestBody,
    SessionTypeHandlerRequestBody,
    SessionsResponse,
    SessionsWithPagination,
    StatusMessage,
    SummaryConfig,
    SummaryExperimentalConfig,
    UpdateAutomationDescriptionRequest,
    VisualAnalysisConfig,
    WindowEventMessage,
    WindowIDData,
    WindowIDDataResponse,
    WindowInfo,
    WindowLoadURLV1Body,
    WindowResponse,
)
```

# Automations

Methods:

- <code title="get /automations">client.automations.<a href="./src/airtop_core/resources/automations.py">list</a>() -> <a href="./src/airtop_core/types/shared/list_automations_output.py">ListAutomationsOutput</a></code>
- <code title="delete /automations/{automationId}">client.automations.<a href="./src/airtop_core/resources/automations.py">delete</a>(automation_id) -> <a href="./src/airtop_core/types/shared/delete_automation_response.py">object</a></code>
- <code title="get /automations/{automationId}">client.automations.<a href="./src/airtop_core/resources/automations.py">get</a>(automation_id) -> <a href="./src/airtop_core/types/shared/automation_data.py">AutomationData</a></code>
- <code title="put /automations/description">client.automations.<a href="./src/airtop_core/resources/automations.py">update_description</a>(\*\*<a href="src/airtop_core/types/automation_update_description_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/automation_data.py">AutomationData</a></code>

# Files

Methods:

- <code title="post /files">client.files.<a href="./src/airtop_core/resources/files.py">create_file</a>(\*\*<a href="src/airtop_core/types/file_create_file_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/create_file_response.py">CreateFileResponse</a></code>
- <code title="get /files/{id}">client.files.<a href="./src/airtop_core/resources/files.py">get</a>(id) -> <a href="./src/airtop_core/types/shared/get_file_response.py">GetFileResponse</a></code>

# Profile

Methods:

- <code title="delete /profiles">client.profile.<a href="./src/airtop_core/resources/profile.py">delete</a>(\*\*<a href="src/airtop_core/types/profile_delete_params.py">params</a>) -> None</code>
- <code title="get /profile/{name}">client.profile.<a href="./src/airtop_core/resources/profile.py">get</a>(name) -> <a href="./src/airtop_core/types/shared/profile_output.py">ProfileOutput</a></code>
- <code title="post /profiles-rename">client.profile.<a href="./src/airtop_core/resources/profile.py">rename</a>(\*\*<a href="src/airtop_core/types/profile_rename_params.py">params</a>) -> None</code>

# Requests

Methods:

- <code title="get /requests/{requestId}/status">client.requests.<a href="./src/airtop_core/resources/requests.py">get_request_status</a>(request_id) -> <a href="./src/airtop_core/types/shared/request_status_response.py">RequestStatusResponse</a></code>

# Sessions

Types:

```python
from airtop_core.types import SessionGetEventsResponse
```

Methods:

- <code title="post /sessions">client.sessions.<a href="./src/airtop_core/resources/sessions.py">create</a>(\*\*<a href="src/airtop_core/types/session_create_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/session_response.py">SessionResponse</a></code>
- <code title="get /sessions">client.sessions.<a href="./src/airtop_core/resources/sessions.py">list</a>(\*\*<a href="src/airtop_core/types/session_list_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/sessions_response.py">SessionsResponse</a></code>
- <code title="get /sessions/{id}">client.sessions.<a href="./src/airtop_core/resources/sessions.py">get</a>(id) -> <a href="./src/airtop_core/types/shared/session_response.py">SessionResponse</a></code>
- <code title="get /sessions/{id}/events">client.sessions.<a href="./src/airtop_core/resources/sessions.py">get_events</a>(id, \*\*<a href="src/airtop_core/types/session_get_events_params.py">params</a>) -> <a href="./src/airtop_core/types/session_get_events_response.py">SessionGetEventsResponse</a></code>
- <code title="put /sessions/{sessionId}/save-profile-on-termination/{profileName}">client.sessions.<a href="./src/airtop_core/resources/sessions.py">save_profile_on_termination</a>(profile_name, \*, session_id) -> None</code>
- <code title="delete /sessions/{id}">client.sessions.<a href="./src/airtop_core/resources/sessions.py">terminate</a>(id) -> None</code>

# Windows

Methods:

- <code title="post /sessions/{sessionId}/windows">client.windows.<a href="./src/airtop_core/resources/windows.py">create</a>(session_id, \*\*<a href="src/airtop_core/types/window_create_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/window_id_data_response.py">WindowIDDataResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/click">client.windows.<a href="./src/airtop_core/resources/windows.py">click</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_click_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="delete /sessions/{sessionId}/windows/{windowId}">client.windows.<a href="./src/airtop_core/resources/windows.py">close</a>(window_id, \*, session_id) -> <a href="./src/airtop_core/types/shared/window_id_data_response.py">WindowIDDataResponse</a></code>
- <code title="get /sessions/{sessionId}/windows/{windowId}">client.windows.<a href="./src/airtop_core/resources/windows.py">get</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_get_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/window_response.py">WindowResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/hover">client.windows.<a href="./src/airtop_core/resources/windows.py">hover</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_hover_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}">client.windows.<a href="./src/airtop_core/resources/windows.py">load_url</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_load_url_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/operation_outcome_response.py">OperationOutcomeResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/monitor">client.windows.<a href="./src/airtop_core/resources/windows.py">monitor</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_monitor_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/page-query">client.windows.<a href="./src/airtop_core/resources/windows.py">page_query</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_page_query_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/paginated-extraction">client.windows.<a href="./src/airtop_core/resources/windows.py">paginated_extraction</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_paginated_extraction_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/prompt-content">client.windows.<a href="./src/airtop_core/resources/windows.py">prompt_content</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_prompt_content_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/scrape-content">client.windows.<a href="./src/airtop_core/resources/windows.py">scrape</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_scrape_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/scrape_response.py">ScrapeResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/screenshot">client.windows.<a href="./src/airtop_core/resources/windows.py">screenshot</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_screenshot_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/scroll">client.windows.<a href="./src/airtop_core/resources/windows.py">scroll</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_scroll_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/summarize-content">client.windows.<a href="./src/airtop_core/resources/windows.py">summarize</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_summarize_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
- <code title="post /sessions/{sessionId}/windows/{windowId}/type">client.windows.<a href="./src/airtop_core/resources/windows.py">type</a>(window_id, \*, session_id, \*\*<a href="src/airtop_core/types/window_type_params.py">params</a>) -> <a href="./src/airtop_core/types/shared/ai_prompt_response.py">AIPromptResponse</a></code>
