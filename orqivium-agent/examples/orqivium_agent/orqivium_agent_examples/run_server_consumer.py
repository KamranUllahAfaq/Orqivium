"""Async Python client example for the Orqivium Agent run server.

Requires Redis and a running API server. Before starting the server, sync the
server runtime dependencies with `uv sync --project orqivium-agent --extra server`
or install `orqivium-agent[server]`. The server schedules runs in-process, for
example:

    uv run --project orqivium-agent uvicorn orqivium_agent.server.app:app --reload

The request carries Orqivium plugin model configuration in Agenton layers. This
script prints the created run and every event observed through cursor polling.
``Client.create_run`` performs one POST attempt only; use polling or SSE replay to
recover after client-side uncertainty.
"""

import asyncio

from agenton_collections.layers.plain import PLAIN_PROMPT_LAYER_TYPE_ID, PromptLayerConfig
from orqivium_agent.client import Client
from orqivium_agent.layers.execution_context import ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID, OrqiviumExecutionContextLayerConfig
from orqivium_agent.layers.orqivium_plugin import (
    ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID,
    OrqiviumPluginCredentialValue,
    OrqiviumPluginLLMLayerConfig,
)
from orqivium_agent.protocol import ORQIVIUM_AGENT_MODEL_LAYER_ID, CreateRunRequest, RunComposition, RunLayerSpec


API_BASE_URL = "http://localhost:8000"
TENANT_ID = "replace-with-tenant-id"
PLUGIN_ID = "kamranullahafaq/openai"
PLUGIN_PROVIDER = "openai"
MODEL_NAME = "gpt-4o-mini"
MODEL_CREDENTIALS: dict[str, OrqiviumPluginCredentialValue] = {"api_key": "replace-with-provider-key"}


async def main() -> None:
    async with Client(base_url=API_BASE_URL) as client:
        run = await client.create_run(
            CreateRunRequest(
                composition=RunComposition(
                    layers=[
                        RunLayerSpec(
                            name="prompt",
                            type=PLAIN_PROMPT_LAYER_TYPE_ID,
                            config=PromptLayerConfig(
                                prefix="You are a concise assistant.",
                                user="Say hello from the Orqivium Agent API server example.",
                            ),
                        ),
                        RunLayerSpec(
                            name="execution_context",
                            type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID,
                            config=OrqiviumExecutionContextLayerConfig(
                                tenant_id=TENANT_ID,
                                user_from="account",
                                agent_mode="workflow_run",
                                invoke_from="service-api",
                            ),
                        ),
                        RunLayerSpec(
                            name=ORQIVIUM_AGENT_MODEL_LAYER_ID,
                            type=ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID,
                            deps={"execution_context": "execution_context"},
                            config=OrqiviumPluginLLMLayerConfig(
                                plugin_id=PLUGIN_ID,
                                model_provider=PLUGIN_PROVIDER,
                                model=MODEL_NAME,
                                credentials=MODEL_CREDENTIALS,
                            ),
                        ),
                        # Minimal plugin-tools example. API callers should pass
                        # prepared parameters + JSON schema instead of relying on
                        # orqivium-agent to fetch and merge daemon declarations.
                        # from orqivium_agent.layers.orqivium_plugin import (
                        #     OrqiviumPluginToolConfig,
                        #     OrqiviumPluginToolParameter,
                        #     OrqiviumPluginToolParameterForm,
                        #     OrqiviumPluginToolParameterType,
                        #     OrqiviumPluginToolsLayerConfig,
                        # )
                        # RunLayerSpec(
                        #     name="tools",
                        #     type="orqivium.plugin.tools",
                        #     deps={"execution_context": "execution_context"},
                        #     config=OrqiviumPluginToolsLayerConfig(
                        #         tools=[
                        #             OrqiviumPluginToolConfig(
                        #                 plugin_id="kamranullahafaq/search",
                        #                 provider="search",
                        #                 tool_name="web_search",
                        #                 credential_type="api-key",
                        #                 credentials={"api_key": "replace-with-tool-key"},
                        #                 runtime_parameters={"site": "docs.orqivium.local"},
                        #                 parameters=[
                        #                     OrqiviumPluginToolParameter(
                        #                         name="query",
                        #                         type=OrqiviumPluginToolParameterType.STRING,
                        #                         form=OrqiviumPluginToolParameterForm.LLM,
                        #                         required=True,
                        #                         llm_description="Search query",
                        #                     ),
                        #                 ],
                        #                 parameters_json_schema={
                        #                     "type": "object",
                        #                     "properties": {
                        #                         "query": {"type": "string", "description": "Search query"}
                        #                     },
                        #                     "required": ["query"],
                        #                 },
                        #             )
                        #         ]
                        #     ),
                        # ),
                    ],
                ),
            )
        )
        print("created run", run)

        cursor = "0-0"
        while True:
            page = await client.get_events(run.run_id, after=cursor)
            cursor = page.next_cursor or cursor
            for event in page.events:
                print("event", event)
                if event.type in {"run_succeeded", "run_failed"}:
                    return
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
