# Get started with Orqivium Agent

This guide walks through the smallest end-to-end path for the current Orqivium Agent
runtime: install dependencies, configure the server, start it, then use the Python
client to create one plugin-daemon-backed run.

## Prerequisites

Install or prepare:

- Python 3.12 or newer
- `uv`
- Redis
- a reachable Orqivium plugin daemon
- a plugin/provider already available through that plugin daemon, such as
  `kamranullahafaq/openai`

## Install dependencies

From the repository root, enter the `orqivium-agent` package and install all extras
and dependency groups:

```bash
cd orqivium-agent
uv sync --all-extras --all-groups
```

Only the `server` extra is required to run the API server, but installing all
extras and groups gives you the local test, docs, and server dependencies in one
environment.

## Start Redis

Skip this step if you already have a reachable Redis instance.

```bash
docker run -d \
  --name orqivium-agent-redis \
  -p 6379:6379 \
  redis:7-alpine
```

## Configure the server

Create or update `.env` in the `orqivium-agent` directory:

```bash
cat > .env <<'EOF'
ORQIVIUM_AGENT_REDIS_URL=redis://localhost:6379/0
ORQIVIUM_AGENT_REDIS_PREFIX=orqivium-agent

ORQIVIUM_AGENT_PLUGIN_DAEMON_URL=http://localhost:5002
ORQIVIUM_AGENT_PLUGIN_DAEMON_API_KEY=replace-with-plugin-daemon-server-key

ORQIVIUM_AGENT_INNER_API_URL=http://localhost:5001
ORQIVIUM_AGENT_INNER_API_KEY=replace-with-orqivium-inner-api-key-for-plugin
EOF
```

The minimum settings are:

- `ORQIVIUM_AGENT_REDIS_URL`: Redis connection URL used for run records and event
  streams.
- `ORQIVIUM_AGENT_REDIS_PREFIX`: Redis key prefix for this server.
- `ORQIVIUM_AGENT_PLUGIN_DAEMON_URL`: base URL for the Orqivium plugin daemon.
- `ORQIVIUM_AGENT_PLUGIN_DAEMON_API_KEY`: API key sent by the server to the plugin
  daemon. In a Orqivium Docker setup this is usually the value previously configured
  as `PLUGIN_DAEMON_KEY`.
- `ORQIVIUM_AGENT_INNER_API_URL`: Orqivium API service root for `/inner/api/...` calls.
- `ORQIVIUM_AGENT_INNER_API_KEY`: API key sent to Orqivium API inner plugin endpoints.
  In Docker this should match `PLUGIN_ORQIVIUM_INNER_API_KEY`, which maps to Orqivium
  API `INNER_API_KEY_FOR_PLUGIN`.

See `.example.env` for the full server settings template.

If you plan to run `orqivium.shell`, also configure `ORQIVIUM_AGENT_SHELLCTL_ENTRYPOINT`
and, when shell jobs need to call back with the `orqivium-agent` command, set
`ORQIVIUM_AGENT_STUB_API_BASE_URL`. The supplied default configs include a
development `ORQIVIUM_AGENT_SERVER_SECRET_KEY`, but production deployments should
override it with a unique 32-byte base64url value as documented in `.example.env`.

## Start the Orqivium Agent server

For a normal local server process:

```bash
make serve
```

For development with uvicorn reload:

```bash
make dev
```

Both commands serve the API at:

```text
http://127.0.0.1:8000
```

The equivalent development command is:

```bash
uv run --extra server uvicorn orqivium_agent.server.app:app \
  --host 127.0.0.1 \
  --port 8000 \
  --reload
```

`ServerSettings` reads `.env` from the current `orqivium-agent` directory, or from
`orqivium-agent/.env` when the command is run from the repository root.

## Create a Python client example

In another shell, keep working from the `orqivium-agent` directory. Create
`run_orqivium_agent_client.py` with the example below, then replace the placeholder
tenant id and provider credential values.

```python {test="skip" lint="skip"}
import asyncio
import json
import sys

from agenton_collections.layers.plain import PLAIN_PROMPT_LAYER_TYPE_ID, PromptLayerConfig
from orqivium_agent.client import Client
from orqivium_agent.layers.execution_context import ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID, OrqiviumExecutionContextLayerConfig
from orqivium_agent.layers.orqivium_plugin import (
    ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID,
    OrqiviumPluginLLMLayerConfig,
)
from orqivium_agent.protocol import ORQIVIUM_AGENT_MODEL_LAYER_ID, CreateRunRequest, RunComposition, RunLayerSpec


API_BASE_URL = "http://127.0.0.1:8000"

TENANT_ID = "replace-with-tenant-id"
PLUGIN_ID = "kamranullahafaq/openai"
USER_ID: str | None = None

# Keep these aligned with ORQIVIUM_AGENT_PROVIDER and ORQIVIUM_AGENT_MODEL_NAME in orqivium-agent/.env.
MODEL_PROVIDER = "replace-with-provider-from-orqivium-agent-env"
MODEL_NAME = "replace-with-model-from-orqivium-agent-env"
MODEL_CREDENTIALS: dict[str, str | int | float | bool | None] = {
    "api_key": "replace-with-provider-key",
}

SYSTEM_PROMPT = "You are a concise assistant."
USER_PROMPT = "用一句话介绍 Orqivium Agent。"


def build_request() -> CreateRunRequest:
    return CreateRunRequest(
        composition=RunComposition(
            layers=[
                RunLayerSpec(
                    name="prompt",
                    type=PLAIN_PROMPT_LAYER_TYPE_ID,
                    config=PromptLayerConfig(prefix=SYSTEM_PROMPT, user=USER_PROMPT),
                ),
                RunLayerSpec(
                    name="execution_context",
                    type=ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID,
                    config=OrqiviumExecutionContextLayerConfig(
                        tenant_id=TENANT_ID,
                        user_id=USER_ID,
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
                        credentials=MODEL_CREDENTIALS,
                    ),
                ),
            ],
        ),
    )


async def main() -> int:
    async with Client(base_url=API_BASE_URL, stream_timeout=None) as client:
        run = await client.create_run(build_request())
        print(f"created run: {run.run_id}, status={run.status}")

        async for event in client.stream_events(run.run_id):
            print(event.model_dump_json(indent=2))

            if event.type == "run_succeeded":
                print("final output:")
                print(json.dumps(event.data.output, ensure_ascii=False, indent=2))
                return 0

            if event.type == "run_failed":
                print(f"run failed: {event.data.error}", file=sys.stderr)
                return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
```

## Run the client example

The server-side `.env` controls how Orqivium Agent reaches the plugin daemon. The
client example controls which tenant/plugin/provider/model and provider
credentials the run uses.

Run the example from the `orqivium-agent` directory:

```bash
uv run python ./run_orqivium_agent_client.py
```

The shape of `MODEL_CREDENTIALS` depends on the selected plugin provider's
credential schema. The `{"api_key":"..."}` value above is only an OpenAI-style
example.

Set `MODEL_PROVIDER` and `MODEL_NAME` to the same values as
`ORQIVIUM_AGENT_PROVIDER` and `ORQIVIUM_AGENT_MODEL_NAME` in `orqivium-agent/.env`.

## Troubleshooting

If the run fails, check these items first:

1. Redis is running and reachable from the Orqivium Agent server.
2. The Orqivium Agent server is listening on `127.0.0.1:8000`.
3. `ORQIVIUM_AGENT_PLUGIN_DAEMON_URL` points to the correct plugin daemon.
4. `ORQIVIUM_AGENT_PLUGIN_DAEMON_API_KEY` matches the plugin daemon server key.
5. `PLUGIN_ID`, `MODEL_PROVIDER`, and `MODEL_NAME` in the client example match
   the corresponding values configured in `orqivium-agent/.env` and a provider
   available through the plugin daemon.
6. `MODEL_CREDENTIALS` matches that provider's credential schema.
