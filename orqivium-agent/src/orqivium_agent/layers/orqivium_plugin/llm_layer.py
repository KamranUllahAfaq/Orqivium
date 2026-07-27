"""Orqivium plugin LLM model layer.

This layer owns model capability resolution for Orqivium plugin-backed LLMs. It
depends on ``OrqiviumExecutionContextLayer`` for shared daemon settings through
Agenton's direct dependency binding and returns a Pydantic AI model adapter
configured from the public LLM layer DTO. Runtime code supplies the FastAPI
lifespan-owned shared HTTP client to ``get_model``; the layer does not own or
discover live resources. The daemon provider carries plugin transport identity,
while the DTO's ``model_provider`` is passed to the adapter as request-level
model identity.
"""

from dataclasses import dataclass
from typing import ClassVar

import httpx
from typing_extensions import Self, override

from agenton.layers import LayerDeps, PlainLayer
from orqivium_agent.adapters.llm import OrqiviumLLMAdapterModel
from orqivium_agent.layers.orqivium_plugin.configs import ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID, OrqiviumPluginLLMLayerConfig
from orqivium_agent.layers.execution_context.layer import OrqiviumExecutionContextLayer


class OrqiviumPluginLLMDeps(LayerDeps):
    """Dependencies required by ``OrqiviumPluginLLMLayer``."""

    execution_context: OrqiviumExecutionContextLayer  # pyright: ignore[reportUninitializedInstanceVariable]


@dataclass(slots=True)
class OrqiviumPluginLLMLayer(PlainLayer[OrqiviumPluginLLMDeps, OrqiviumPluginLLMLayerConfig]):
    """Layer that creates the Orqivium plugin-daemon Pydantic AI model."""

    type_id: ClassVar[str | None] = ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID

    config: OrqiviumPluginLLMLayerConfig

    @classmethod
    @override
    def from_config(cls, config: OrqiviumPluginLLMLayerConfig) -> Self:
        """Create the LLM layer from validated public config."""
        return cls(config=config)

    def get_model(self, *, http_client: httpx.AsyncClient) -> OrqiviumLLMAdapterModel:
        """Return the configured model using the directly bound execution context."""
        provider = self.deps.execution_context.create_daemon_provider(
            plugin_id=self.config.plugin_id,
            http_client=http_client,
        )
        return OrqiviumLLMAdapterModel(
            model=self.config.model,
            daemon_provider=provider,
            model_provider=self.config.model_provider,
            credentials=dict(self.config.credentials),
            model_settings=self.config.model_settings,
        )


__all__ = ["OrqiviumPluginLLMDeps", "OrqiviumPluginLLMLayer"]
