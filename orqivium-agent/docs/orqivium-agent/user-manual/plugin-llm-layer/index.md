# Plugin LLM layer

The plugin LLM layer selects the plugin package, model provider, model name,
provider credentials, and optional model settings for the current run. Orqivium
Agent reads the model from the reserved layer name `llm`.

It must depend on an [execution context layer](../execution-context-layer/index.md),
because that layer supplies the daemon identity and transport context.

## Config fields

| Field | Type | Meaning |
| --- | --- | --- |
| `plugin_id` | `str` | Plugin package id, for example `kamranullahafaq/openai`. |
| `model_provider` | `str` | Provider name inside `plugin_id`. Use the value of `ORQIVIUM_AGENT_PROVIDER` from `orqivium-agent/.env`. |
| `model` | `str` | Model name. Use the value of `ORQIVIUM_AGENT_MODEL_NAME` from `orqivium-agent/.env`. |
| `credentials` | `dict[str, str \| int \| float \| bool \| None]` | Provider-specific credential object. |
| `model_settings` | `ModelSettings \| None` | Optional pydantic-ai model settings. |

The plugin LLM layer type id is `orqivium.plugin.llm`.

## Basic usage

```python {test="skip" lint="skip"}
from orqivium_agent.layers.orqivium_plugin import ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID, OrqiviumPluginLLMLayerConfig
from orqivium_agent.protocol import ORQIVIUM_AGENT_MODEL_LAYER_ID, RunLayerSpec


MODEL_PROVIDER = "replace-with-provider-from-orqivium-agent-env"
MODEL_NAME = "replace-with-model-from-orqivium-agent-env"
PLUGIN_ID = "kamranullahafaq/openai"

llm_layer = RunLayerSpec(
    name=ORQIVIUM_AGENT_MODEL_LAYER_ID,
    type=ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID,
    deps={"execution_context": "execution_context"},
    config=OrqiviumPluginLLMLayerConfig(
        plugin_id=PLUGIN_ID,
        model_provider=MODEL_PROVIDER,
        model=MODEL_NAME,
        credentials={"api_key": "replace-with-provider-key"},
    ),
)
```

`deps={"execution_context": "execution_context"}` means: bind the LLM layer's
dependency field named `execution_context` to the composition layer named
`execution_context`.

Set `MODEL_PROVIDER` and `MODEL_NAME` to the same values as
`ORQIVIUM_AGENT_PROVIDER` and `ORQIVIUM_AGENT_MODEL_NAME` in `orqivium-agent/.env`.

## Complete minimal model composition

Most runs include a prompt, execution-context layer, and LLM layer:

```python {test="skip" lint="skip"}
from agenton_collections.layers.plain import PLAIN_PROMPT_LAYER_TYPE_ID, PromptLayerConfig
from orqivium_agent.layers.execution_context import ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID, OrqiviumExecutionContextLayerConfig
from orqivium_agent.layers.orqivium_plugin import (
    ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID,
    OrqiviumPluginLLMLayerConfig,
)
from orqivium_agent.protocol import ORQIVIUM_AGENT_MODEL_LAYER_ID, RunComposition, RunLayerSpec


MODEL_PROVIDER = "replace-with-provider-from-orqivium-agent-env"
MODEL_NAME = "replace-with-model-from-orqivium-agent-env"
PLUGIN_ID = "kamranullahafaq/openai"

composition = RunComposition(
    layers=[
        RunLayerSpec(
            name="prompt",
            type=PLAIN_PROMPT_LAYER_TYPE_ID,
            config=PromptLayerConfig(prefix="You are concise.", user="Say hello."),
        ),
        RunLayerSpec(
            name="execution_context",
            type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID,
            config=OrqiviumExecutionContextLayerConfig(
                tenant_id="replace-with-tenant-id",
                invoke_from="workflow_run",
            ),
        ),
        RunLayerSpec(
            name=ORQIVIUM_AGENT_MODEL_LAYER_ID,
            type=ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID,
            deps={"execution_context": "execution_context"},
            config=OrqiviumPluginLLMLayerConfig(
                plugin_id=PLUGIN_ID,
                model_provider=MODEL_PROVIDER,
                model=MODEL_NAME,
                credentials={"api_key": "replace-with-provider-key"},
            ),
        ),
    ]
)
```

## Notes

- The model layer must use the reserved name `llm` (`ORQIVIUM_AGENT_MODEL_LAYER_ID`).
- `plugin_id` belongs here because model calls are plugin-specific business
  calls. The shared execution-context layer only carries Orqivium run and
  tenant/user daemon context.
- Credential shape depends on the selected plugin provider; the OpenAI-style
  `api_key` field above is only an example.
- Client-submitted model credentials remain in the scheduled request memory and
  are not part of run records or session snapshots.
