import pytest
from pydantic import ValidationError

import orqivium_agent.layers.orqivium_core_tools as orqivium_core_tools_exports
from orqivium_agent.layers.orqivium_core_tools import OrqiviumCoreToolConfig, OrqiviumCoreToolsLayerConfig


def test_orqivium_core_tools_package_exports_client_safe_config_symbols_only() -> None:
    assert orqivium_core_tools_exports.__all__ == [
        "ORQIVIUM_CORE_TOOLS_LAYER_TYPE_ID",
        "OrqiviumCoreToolConfig",
        "OrqiviumCoreToolProviderType",
        "OrqiviumCoreToolsLayerConfig",
    ]
    assert orqivium_core_tools_exports.ORQIVIUM_CORE_TOOLS_LAYER_TYPE_ID == "orqivium.core.tools"


def test_orqivium_core_tools_layer_config_accepts_supported_provider_types() -> None:
    config = OrqiviumCoreToolsLayerConfig.model_validate(
        {
            "tools": [
                {
                    "provider_type": "plugin",
                    "provider_id": "kamranullahafaq/search/search",
                    "tool_name": "search",
                },
                {
                    "provider_type": "builtin",
                    "provider_id": "audio",
                    "tool_name": "transcribe",
                },
                {
                    "provider_type": "api",
                    "provider_id": "weather",
                    "tool_name": "forecast",
                },
                {
                    "provider_type": "workflow",
                    "provider_id": "workflow-tool",
                    "tool_name": "run_workflow",
                },
                {
                    "provider_type": "mcp",
                    "provider_id": "server-1",
                    "tool_name": "search_docs",
                },
            ]
        }
    )

    assert [tool.provider_type for tool in config.tools] == ["plugin", "builtin", "api", "workflow", "mcp"]


def test_orqivium_core_tool_config_rejects_unsupported_provider_types() -> None:
    with pytest.raises(ValidationError, match="provider_type"):
        _ = OrqiviumCoreToolConfig.model_validate(
            {
                "provider_type": "app",
                "provider_id": "app-tool",
                "tool_name": "run",
            }
        )
