"""Synchronous Python client example for the Orqivium Agent run server.

Requires the same running FastAPI server as the async examples. Before starting
that server, sync the server runtime dependencies with
`uv sync --project orqivium-agent --extra server` or install
`orqivium-agent[server]`. ``create_run_sync`` does not retry ``POST /runs``; if a
timeout occurs, inspect server state or create a new run explicitly rather than
assuming the original request was not accepted.
"""

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


def main() -> None:
    with Client(base_url=API_BASE_URL) as client:
        run = client.create_run_sync(
            CreateRunRequest(
                composition=RunComposition(
                    layers=[
                        RunLayerSpec(
                            name="prompt",
                            type=PLAIN_PROMPT_LAYER_TYPE_ID,
                            config=PromptLayerConfig(
                                prefix="You are a concise assistant.",
                                user="Say hello from the synchronous Orqivium Agent client example.",
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
        terminal = client.wait_run_sync(run.run_id, poll_interval_seconds=0.5)
        print("terminal status", terminal)


if __name__ == "__main__":
    main()
