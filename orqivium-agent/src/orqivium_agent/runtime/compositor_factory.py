"""Safe Agenton compositor construction for API-submitted configs.

Only explicitly allowed provider type ids are constructible here. The default
provider set contains prompt layers, the optional pydantic-ai history layer, the
state-free Orqivium structured output layer, the optional Orqivium ask-human layer, the
Orqivium execution-context layer, the stateful Orqivium shell layer, and the Orqivium
plugin/knowledge business-layer family:

- ``orqivium.config`` for Agent Soul-backed config assets + eager pull,
- ``orqivium.execution_context`` for shared tenant/user/run daemon context,
- ``orqivium.shell`` for shellctl-backed shell job control,
- ``orqivium.plugin.llm`` for plugin-backed model selection,
- ``orqivium.plugin.tools`` for prepared plugin tool exposure, and
- ``orqivium.core.tools`` for API-routed Orqivium tool exposure, and
- ``orqivium.knowledge_base`` for inner-API-backed knowledge search tools.

Public DTOs provide Orqivium context plus plugin/model/tool data, while server-only
plugin daemon settings and Orqivium API inner settings are injected through provider
factories. An already-selected shell provider (shellctl or enterprise, built at
the runtime boundary) and the Agent Stub URL/token factory are injected for
``OrqiviumShellLayer``; a ``None`` shell provider leaves the shell layer disabled.
The resulting ``Compositor``
remains Agenton state-only at the snapshot boundary: live resources such as
HTTP clients are injected by runtime-owned providers, may be held on active
layer instances inside ``resource_context()``, and never enter session
snapshots.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from orqivium_agent.adapters.shell.protocols import ShellProviderProtocol

from pydantic_ai.messages import UserContent

from agenton.compositor import Compositor, CompositorConfig, LayerProvider, LayerProviderInput
from agenton.layers.types import AllPromptTypes, AllToolTypes, AllUserPromptTypes, PydanticAIPrompt, PydanticAITool
from agenton_collections.layers.pydantic_ai import PydanticAIHistoryLayer
from agenton_collections.layers.plain.basic import PromptLayer
from agenton_collections.transformers.pydantic_ai import PYDANTIC_AI_TRANSFORMERS
from orqivium_agent.agent_stub.shell_env import ShellAgentStubTokenFactory
from orqivium_agent.layers.ask_human.layer import OrqiviumAskHumanLayer
from orqivium_agent.layers.config.layer import OrqiviumConfigLayer
from orqivium_agent.layers.orqivium_core_tools.configs import OrqiviumCoreToolsLayerConfig
from orqivium_agent.layers.orqivium_core_tools.layer import OrqiviumCoreToolsLayer
from orqivium_agent.layers.orqivium_plugin.llm_layer import OrqiviumPluginLLMLayer
from orqivium_agent.layers.orqivium_plugin.configs import OrqiviumPluginToolsLayerConfig
from orqivium_agent.layers.orqivium_plugin.tools_layer import OrqiviumPluginToolsLayer
from orqivium_agent.layers.drive.layer import OrqiviumDriveLayer
from orqivium_agent.layers.execution_context.configs import OrqiviumExecutionContextLayerConfig
from orqivium_agent.layers.execution_context.layer import OrqiviumExecutionContextLayer
from orqivium_agent.layers.knowledge.configs import OrqiviumKnowledgeBaseLayerConfig
from orqivium_agent.layers.knowledge.layer import OrqiviumKnowledgeBaseLayer
from orqivium_agent.layers.output.output_layer import OrqiviumOutputLayer
from orqivium_agent.layers.shell.configs import OrqiviumShellLayerConfig
from orqivium_agent.layers.shell.layer import OrqiviumShellLayer

type OrqiviumAgentLayerProvider = LayerProvider[Any]


def create_default_layer_providers(
    *,
    plugin_daemon_url: str = "http://localhost:5002",
    plugin_daemon_api_key: str = "",
    inner_api_url: str = "http://localhost:5001",
    inner_api_key: str = "",
    shell_provider: ShellProviderProtocol | None = None,
    shell_home_root: str = "/home",
    shell_redact_patterns: list[str] | None = None,
    agent_stub_api_base_url: str | None = None,
    agent_stub_token_factory: ShellAgentStubTokenFactory | None = None,
) -> tuple[OrqiviumAgentLayerProvider, ...]:
    """Return the server provider set of safe config-constructible layers."""
    return (
        LayerProvider.from_layer_type(PromptLayer),
        LayerProvider.from_layer_type(PydanticAIHistoryLayer),
        LayerProvider.from_layer_type(OrqiviumOutputLayer),
        LayerProvider.from_layer_type(OrqiviumAskHumanLayer),
        LayerProvider.from_layer_type(OrqiviumConfigLayer),
        LayerProvider.from_layer_type(OrqiviumDriveLayer),
        LayerProvider.from_factory(
            layer_type=OrqiviumExecutionContextLayer,
            create=lambda config: OrqiviumExecutionContextLayer.from_config_with_settings(
                OrqiviumExecutionContextLayerConfig.model_validate(config),
                daemon_url=plugin_daemon_url,
                daemon_api_key=plugin_daemon_api_key,
            ),
        ),
        LayerProvider.from_factory(
            layer_type=OrqiviumShellLayer,
            create=lambda config: OrqiviumShellLayer.from_config_with_settings(
                OrqiviumShellLayerConfig.model_validate(config),
                shell_provider=shell_provider,
                shell_home_root=shell_home_root,
                shell_redact_patterns=shell_redact_patterns or [],
                agent_stub_api_base_url=agent_stub_api_base_url,
                agent_stub_token_factory=agent_stub_token_factory,
            ),
        ),
        LayerProvider.from_layer_type(OrqiviumPluginLLMLayer),
        LayerProvider.from_factory(
            layer_type=OrqiviumPluginToolsLayer,
            create=lambda config: OrqiviumPluginToolsLayer.from_config_with_settings(
                OrqiviumPluginToolsLayerConfig.model_validate(config),
                inner_api_url=inner_api_url,
                inner_api_key=inner_api_key,
            ),
        ),
        LayerProvider.from_factory(
            layer_type=OrqiviumCoreToolsLayer,
            create=lambda config: OrqiviumCoreToolsLayer.from_config_with_settings(
                OrqiviumCoreToolsLayerConfig.model_validate(config),
                inner_api_url=inner_api_url,
                inner_api_key=inner_api_key,
            ),
        ),
        LayerProvider.from_factory(
            layer_type=OrqiviumKnowledgeBaseLayer,
            create=lambda config: OrqiviumKnowledgeBaseLayer.from_config_with_settings(
                OrqiviumKnowledgeBaseLayerConfig.model_validate(config),
                inner_api_url=inner_api_url,
                inner_api_key=inner_api_key,
            ),
        ),
    )


def build_pydantic_ai_compositor(
    config: CompositorConfig,
    *,
    providers: Sequence[LayerProviderInput],
    node_providers: Mapping[str, LayerProviderInput] | None = None,
) -> Compositor[
    PydanticAIPrompt[object],
    PydanticAITool[object],
    AllPromptTypes,
    AllToolTypes,
    UserContent,
    AllUserPromptTypes,
]:
    """Build a Pydantic AI-ready compositor from a validated graph config.

    Prompt, user prompt, and tool conversion is delegated to Agenton's shared
    pydantic-ai transformer preset so Orqivium Agent does not duplicate conversion
    logic for plain and pydantic-ai layer families. Callers must pass the already
    selected provider set explicitly so provider defaulting stays at outer runtime
    boundaries rather than being duplicated here.
    """
    return cast(
        Compositor[
            PydanticAIPrompt[object],
            PydanticAITool[object],
            AllPromptTypes,
            AllToolTypes,
            UserContent,
            AllUserPromptTypes,
        ],
        Compositor.from_config(
            config,
            providers=providers,
            node_providers=node_providers,
            **PYDANTIC_AI_TRANSFORMERS,  # pyright: ignore[reportArgumentType]
        ),
    )


__all__ = ["OrqiviumAgentLayerProvider", "build_pydantic_ai_compositor", "create_default_layer_providers"]
