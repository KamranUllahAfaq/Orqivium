import pytest
from pydantic import ValidationError

import orqivium_agent.layers.execution_context as execution_context_exports
from orqivium_agent.layers.execution_context import OrqiviumExecutionContextLayerConfig


def test_execution_context_package_exports_client_safe_config_symbols_only() -> None:
    assert execution_context_exports.__all__ == [
        "ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID",
        "OrqiviumExecutionContextAgentConfigVersionKind",
        "OrqiviumExecutionContextAgentMode",
        "OrqiviumExecutionContextInvokeFrom",
        "OrqiviumExecutionContextLayerConfig",
        "OrqiviumExecutionContextUserFrom",
    ]
    assert execution_context_exports.ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID == "orqivium.execution_context"
    assert not hasattr(execution_context_exports, "OrqiviumExecutionContextLayer")


def test_execution_context_accepts_real_invoke_from_user_from_and_agent_mode() -> None:
    config = OrqiviumExecutionContextLayerConfig(
        tenant_id="tenant-1",
        user_id="user-1",
        user_from="end-user",
        invoke_from="web-app",
        agent_mode="agent_app",
    )

    assert config.user_from == "end-user"
    assert config.invoke_from == "web-app"
    assert config.agent_mode == "agent_app"


def test_execution_context_rejects_legacy_agent_mode_in_invoke_from() -> None:
    with pytest.raises(ValidationError):
        _ = OrqiviumExecutionContextLayerConfig.model_validate(
            {
                "tenant_id": "tenant-1",
                "user_from": "account",
                "agent_mode": "workflow_run",
                "invoke_from": "workflow_run",
            }
        )


def test_execution_context_layer_config_forbids_runtime_settings_and_unknown_fields() -> None:
    config = OrqiviumExecutionContextLayerConfig(
        tenant_id="tenant-1",
        user_id="user-1",
        user_from="account",
        workflow_id="workflow-1",
        agent_mode="workflow_run",
        invoke_from="service-api",
    )

    assert config.tenant_id == "tenant-1"
    assert config.user_id == "user-1"
    assert config.user_from == "account"
    assert config.workflow_id == "workflow-1"
    assert config.agent_mode == "workflow_run"
    assert config.invoke_from == "service-api"

    with pytest.raises(ValidationError):
        _ = OrqiviumExecutionContextLayerConfig.model_validate(
            {
                "tenant_id": "tenant-1",
                "user_from": "account",
                "agent_mode": "workflow_run",
                "invoke_from": "service-api",
                "daemon_url": "http://daemon",
            }
        )

    with pytest.raises(ValidationError):
        _ = OrqiviumExecutionContextLayerConfig.model_validate(
            {
                "tenant_id": "tenant-1",
                "user_from": "account",
                "agent_mode": "workflow_run",
                "invoke_from": "service-api",
                "unknown": "value",
            }
        )
