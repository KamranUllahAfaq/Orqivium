from __future__ import annotations

import pytest
from agenton.compositor import CompositorSessionSnapshot
from agenton.compositor.schemas import LayerSessionSnapshot
from agenton.layers.base import LifecycleState
from agenton_collections.layers.plain import PromptLayerConfig
from orqivium_agent.layers.orqivium_core_tools import ORQIVIUM_CORE_TOOLS_LAYER_TYPE_ID
from orqivium_agent.layers.orqivium_plugin import ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID
from orqivium_agent.layers.execution_context import ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID, OrqiviumExecutionContextLayerConfig
from orqivium_agent.layers.shell import ORQIVIUM_SHELL_LAYER_TYPE_ID, OrqiviumShellLayerConfig
from orqivium_agent.protocol import (
    CreateRunRequest,
    RunComposition,
    RunLayerSpec,
    RuntimeLayerSpec,
    build_sandbox_locator_from_layer_specs,
    build_sandbox_locator_from_run_request,
    extract_runtime_layer_specs,
)


def _request() -> CreateRunRequest:
    composition = RunComposition(
        layers=[
            RunLayerSpec(name="prompt", type="plain.prompt", config=PromptLayerConfig(prefix="hi")),
            RunLayerSpec(
                name="execution_context",
                type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID,
                config=OrqiviumExecutionContextLayerConfig(
                    tenant_id="tenant-1",
                    user_from="account",
                    agent_mode="workflow_run",
                    invoke_from="service-api",
                ),
            ),
            RunLayerSpec(name="llm", type=ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID),
            RunLayerSpec(
                name="shell",
                type=ORQIVIUM_SHELL_LAYER_TYPE_ID,
                deps={"execution_context": "execution_context"},
                config=OrqiviumShellLayerConfig(),
            ),
        ]
    )
    snapshot = CompositorSessionSnapshot(
        layers=[
            LayerSessionSnapshot(name="prompt", lifecycle_state=LifecycleState.SUSPENDED, runtime_state={}),
            LayerSessionSnapshot(
                name="execution_context",
                lifecycle_state=LifecycleState.SUSPENDED,
                runtime_state={},
            ),
            LayerSessionSnapshot(name="llm", lifecycle_state=LifecycleState.SUSPENDED, runtime_state={}),
            LayerSessionSnapshot(
                name="shell",
                lifecycle_state=LifecycleState.SUSPENDED,
                runtime_state={"session_id": "abc12ff", "workspace_cwd": "~/workspace/abc12ff"},
            ),
        ]
    )
    return CreateRunRequest(composition=composition, session_snapshot=snapshot)


def test_build_sandbox_locator_from_run_request_filters_to_execution_context_and_shell() -> None:
    locator = build_sandbox_locator_from_run_request(_request())

    assert [layer.name for layer in locator.composition.layers] == ["execution_context", "shell"]
    assert [layer.type for layer in locator.composition.layers] == [
        ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID,
        ORQIVIUM_SHELL_LAYER_TYPE_ID,
    ]
    assert [layer.name for layer in locator.session_snapshot.layers] == ["execution_context", "shell"]


def test_build_sandbox_locator_from_run_request_rejects_missing_session_snapshot() -> None:
    request = _request()
    request.session_snapshot = None

    with pytest.raises(ValueError, match="session_snapshot"):
        build_sandbox_locator_from_run_request(request)


def test_extract_runtime_layer_specs_drops_sensitive_plugin_layers() -> None:
    specs = extract_runtime_layer_specs(_request().composition)

    assert [spec.name for spec in specs] == ["prompt", "execution_context", "shell"]


def test_build_sandbox_locator_from_layer_specs_rejects_missing_shell() -> None:
    with pytest.raises(ValueError, match="shell"):
        build_sandbox_locator_from_layer_specs(
            layer_specs=[RuntimeLayerSpec(name="execution_context", type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID)],
            session_snapshot=CompositorSessionSnapshot(layers=[]),
        )


def test_build_sandbox_locator_from_layer_specs_rejects_missing_snapshot_layer() -> None:
    specs = [
        RuntimeLayerSpec(name="execution_context", type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID),
        RuntimeLayerSpec(name="shell", type=ORQIVIUM_SHELL_LAYER_TYPE_ID, deps={"execution_context": "execution_context"}),
    ]

    with pytest.raises(ValueError, match="session_snapshot"):
        build_sandbox_locator_from_layer_specs(
            layer_specs=specs,
            session_snapshot=CompositorSessionSnapshot(
                layers=[
                    LayerSessionSnapshot(
                        name="execution_context", lifecycle_state=LifecycleState.SUSPENDED, runtime_state={}
                    )
                ]
            ),
        )


def test_build_sandbox_locator_from_layer_specs_rejects_shell_dep_mismatch() -> None:
    specs = [
        RuntimeLayerSpec(name="execution_context", type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID),
        RuntimeLayerSpec(name="shell", type=ORQIVIUM_SHELL_LAYER_TYPE_ID, deps={"execution_context": "wrong-layer"}),
    ]

    with pytest.raises(ValueError, match="depend on the execution_context"):
        build_sandbox_locator_from_layer_specs(
            layer_specs=specs,
            session_snapshot=CompositorSessionSnapshot(
                layers=[
                    LayerSessionSnapshot(
                        name="execution_context",
                        lifecycle_state=LifecycleState.SUSPENDED,
                        runtime_state={},
                    ),
                    LayerSessionSnapshot(
                        name="shell",
                        lifecycle_state=LifecycleState.SUSPENDED,
                        runtime_state={},
                    ),
                ]
            ),
        )


def test_build_sandbox_locator_from_layer_specs_rejects_order_mismatch() -> None:
    specs = [
        RuntimeLayerSpec(name="execution_context", type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID),
        RuntimeLayerSpec(name="shell", type=ORQIVIUM_SHELL_LAYER_TYPE_ID, deps={"execution_context": "execution_context"}),
    ]

    with pytest.raises(ValueError, match="in order"):
        build_sandbox_locator_from_layer_specs(
            layer_specs=specs,
            session_snapshot=CompositorSessionSnapshot(
                layers=[
                    LayerSessionSnapshot(name="shell", lifecycle_state=LifecycleState.SUSPENDED, runtime_state={}),
                    LayerSessionSnapshot(
                        name="execution_context",
                        lifecycle_state=LifecycleState.SUSPENDED,
                        runtime_state={},
                    ),
                ]
            ),
        )


def test_build_sandbox_locator_from_layer_specs_rejects_sensitive_runtime_specs() -> None:
    with pytest.raises(ValueError, match="sensitive"):
        build_sandbox_locator_from_layer_specs(
            layer_specs=[RuntimeLayerSpec(name="llm", type=ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID)],
            session_snapshot=CompositorSessionSnapshot(layers=[]),
        )


def test_build_sandbox_locator_from_layer_specs_rejects_sensitive_core_tool_runtime_specs() -> None:
    with pytest.raises(ValueError, match="sensitive"):
        build_sandbox_locator_from_layer_specs(
            layer_specs=[RuntimeLayerSpec(name="core_tools", type=ORQIVIUM_CORE_TOOLS_LAYER_TYPE_ID)],
            session_snapshot=CompositorSessionSnapshot(layers=[]),
        )
