from enum import StrEnum
from typing import cast

from opentelemetry.util.types import AttributeValue
from pydantic import BaseModel, ConfigDict


class EnterpriseTelemetrySpan(StrEnum):
    WORKFLOW_RUN = "orqivium.workflow.run"
    NODE_EXECUTION = "orqivium.node.execution"
    DRAFT_NODE_EXECUTION = "orqivium.node.execution.draft"


class EnterpriseTelemetryEvent(StrEnum):
    """Event names for enterprise telemetry logs."""

    APP_CREATED = "orqivium.app.created"
    APP_UPDATED = "orqivium.app.updated"
    APP_DELETED = "orqivium.app.deleted"
    FEEDBACK_CREATED = "orqivium.feedback.created"
    WORKFLOW_RUN = "orqivium.workflow.run"
    MESSAGE_RUN = "orqivium.message.run"
    TOOL_EXECUTION = "orqivium.tool.execution"
    MODERATION_CHECK = "orqivium.moderation.check"
    SUGGESTED_QUESTION_GENERATION = "orqivium.suggested_question.generation"
    DATASET_RETRIEVAL = "orqivium.dataset.retrieval"
    GENERATE_NAME_EXECUTION = "orqivium.generate_name.execution"
    PROMPT_GENERATION_EXECUTION = "orqivium.prompt_generation.execution"
    REHYDRATION_FAILED = "orqivium.telemetry.rehydration_failed"


class EnterpriseTelemetryCounter(StrEnum):
    TOKENS = "tokens"
    INPUT_TOKENS = "input_tokens"
    OUTPUT_TOKENS = "output_tokens"
    REQUESTS = "requests"
    ERRORS = "errors"
    FEEDBACK = "feedback"
    DATASET_RETRIEVALS = "dataset_retrievals"
    APP_CREATED = "app_created"
    APP_UPDATED = "app_updated"
    APP_DELETED = "app_deleted"


class EnterpriseTelemetryHistogram(StrEnum):
    WORKFLOW_DURATION = "workflow_duration"
    NODE_DURATION = "node_duration"
    MESSAGE_DURATION = "message_duration"
    MESSAGE_TTFT = "message_ttft"
    TOOL_DURATION = "tool_duration"
    PROMPT_GENERATION_DURATION = "prompt_generation_duration"


class TokenMetricLabels(BaseModel):
    """Unified label structure for all orqivium.token.* metrics.

    All token counters (orqivium.tokens.input, orqivium.tokens.output, orqivium.tokens.total) MUST
    use this exact label set to ensure consistent filtering and aggregation across
    different operation types.

    Attributes:
        tenant_id: Tenant identifier.
        app_id: Application identifier.
        operation_type: Source of token usage (workflow | node_execution | message |
            rule_generate | code_generate | structured_output | instruction_modify).
        model_provider: LLM provider name. Empty string if not applicable (e.g., workflow-level).
        model_name: LLM model name. Empty string if not applicable (e.g., workflow-level).
        node_type: Workflow node type. Empty string unless operation_type=node_execution.

    Usage:
        labels = TokenMetricLabels(
            tenant_id="tenant-123",
            app_id="app-456",
            operation_type=OperationType.WORKFLOW,
            model_provider="",
            model_name="",
            node_type="",
        )
        exporter.increment_counter(
            EnterpriseTelemetryCounter.INPUT_TOKENS,
            100,
            labels.to_dict()
        )

    Design rationale:
        Without this unified structure, tokens get double-counted when querying totals
        because workflow.total_tokens is already the sum of all node tokens. The
        operation_type label allows filtering to separate workflow-level aggregates from
        node-level detail, while keeping the same label cardinality for consistent queries.
    """

    tenant_id: str
    app_id: str
    operation_type: str
    model_provider: str
    model_name: str
    node_type: str

    model_config = ConfigDict(extra="forbid", frozen=True)

    def to_dict(self) -> dict[str, AttributeValue]:
        return cast(
            dict[str, AttributeValue],
            {
                "tenant_id": self.tenant_id,
                "app_id": self.app_id,
                "operation_type": self.operation_type,
                "model_provider": self.model_provider,
                "model_name": self.model_name,
                "node_type": self.node_type,
            },
        )


__all__ = [
    "EnterpriseTelemetryCounter",
    "EnterpriseTelemetryEvent",
    "EnterpriseTelemetryHistogram",
    "EnterpriseTelemetrySpan",
    "TokenMetricLabels",
]
