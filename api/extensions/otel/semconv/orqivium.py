"""Orqivium-specific semantic convention definitions."""


class OrqiviumSpanAttributes:
    """Attribute names for Orqivium-specific spans."""

    APP_ID = "orqivium.app_id"
    """Application identifier."""

    TENANT_ID = "orqivium.tenant_id"
    """Tenant identifier."""

    USER_TYPE = "orqivium.user_type"
    """User type, e.g. Account, EndUser."""

    STREAMING = "orqivium.streaming"
    """Whether streaming response is enabled."""

    WORKFLOW_ID = "orqivium.workflow_id"
    """Workflow identifier."""

    WORKFLOW_ABORT_REASON = "orqivium.workflow.abort.reason"
    """Reason recorded when a workflow run is aborted."""

    INVOKE_FROM = "orqivium.invoke_from"
    """Invocation source, e.g. SERVICE_API, WEB_APP, DEBUGGER."""

    INVOKED_BY = "orqivium.invoked_by"
    """Invoked by, e.g. end_user, account, user."""

    USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
    """Number of input tokens (prompt tokens) used."""

    USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
    """Number of output tokens (completion tokens) generated."""

    USAGE_TOTAL_TOKENS = "gen_ai.usage.total_tokens"
    """Total number of tokens used."""
