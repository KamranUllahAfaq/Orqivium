"""Client-safe DTOs for the Orqivium core-tools Agenton layer.

This layer exposes API-routed tool invocations for the Orqivium-owned provider
families that should execute inside the API service boundary: `plugin`,
`builtin`, `api`, `workflow`, and `mcp`. Prepared parameter declarations and
LLM-facing JSON schema are still sent by the API side so the agent runtime does
not need to inspect provider internals or storage state.
"""

from __future__ import annotations

from typing import ClassVar, Final, Literal

from pydantic import ConfigDict, Field, JsonValue

from agenton.layers import LayerConfig
from orqivium_agent.layers.orqivium_plugin.configs import OrqiviumPluginToolParameter

type OrqiviumCoreToolProviderType = Literal["plugin", "builtin", "api", "workflow", "mcp"]

ORQIVIUM_CORE_TOOLS_LAYER_TYPE_ID: Final[str] = "orqivium.core.tools"


class OrqiviumCoreToolConfig(LayerConfig):
    """Prepared API-routed tool declaration exposed to the model."""

    provider_type: OrqiviumCoreToolProviderType
    provider_id: str
    tool_name: str
    credential_id: str | None = None
    name: str | None = None
    description: str | None = None
    runtime_parameters: dict[str, JsonValue] = Field(default_factory=dict)
    parameters: list[OrqiviumPluginToolParameter] = Field(default_factory=list)
    parameters_json_schema: dict[str, JsonValue] = Field(
        default_factory=lambda: {"type": "object", "properties": {}, "required": []}
    )

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


class OrqiviumCoreToolsLayerConfig(LayerConfig):
    """Public config for the Orqivium core-tools layer."""

    tools: list[OrqiviumCoreToolConfig] = Field(default_factory=list)

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
