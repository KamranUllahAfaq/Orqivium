# Operating the Orqivium Agent Run Server

This guide describes how to run the MVP Orqivium Agent API server. The server is
implemented in `orqivium-agent/src/orqivium_agent/server/app.py` and uses Redis for run
records and per-run event streams only.

## Default local startup

Start Redis, then run one FastAPI/uvicorn process:

```bash
uv run --project orqivium-agent uvicorn orqivium_agent.server.app:app --reload
```

By default, the FastAPI lifespan creates:

- one Redis-backed run store used by HTTP routes
- one shared plugin-daemon `httpx.AsyncClient` used by local run tasks
- one process-local scheduler that starts background `asyncio` run tasks

This means local development needs one uvicorn process plus Redis, and
plugin-backed runs also need a reachable Orqivium plugin daemon. Run execution still
happens outside request handlers, so client disconnects do not cancel the agent
run.

## Configuration

`ServerSettings` loads environment variables with the `ORQIVIUM_AGENT_` prefix. It
also reads `.env` and `orqivium-agent/.env` when present.

| Environment variable | Default | Description |
| --- | --- | --- |
| `ORQIVIUM_AGENT_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL. |
| `ORQIVIUM_AGENT_REDIS_PREFIX` | `orqivium-agent` | Prefix for Redis record and event keys. |
| `ORQIVIUM_AGENT_SHUTDOWN_GRACE_SECONDS` | `30` | Seconds to wait for active local runs during graceful shutdown before cancellation. |
| `ORQIVIUM_AGENT_RUN_RETENTION_SECONDS` | `259200` | Seconds to retain Redis run records and per-run event streams; defaults to 3 days. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_URL` | `http://localhost:5002` | Base URL for the Orqivium plugin daemon. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_API_KEY` | empty | API key sent to the Orqivium plugin daemon. |
| `ORQIVIUM_AGENT_INNER_API_URL` | `http://localhost:5001` | Orqivium API service root used when orqivium-agent calls `/inner/api/...` endpoints. |
| `ORQIVIUM_AGENT_INNER_API_KEY` | empty | API key sent to Orqivium API inner plugin endpoints. Set this to Orqivium API `INNER_API_KEY_FOR_PLUGIN` (Docker: `PLUGIN_ORQIVIUM_INNER_API_KEY`). |
| `ORQIVIUM_AGENT_SHELLCTL_ENTRYPOINT` | empty | Base URL for the shellctl server used by `orqivium.shell`; required when runs include the shell layer. |
| `ORQIVIUM_AGENT_SHELLCTL_AUTH_TOKEN` | empty | Optional bearer token sent to the shellctl server. |
| `ORQIVIUM_AGENT_SHELL_HOME_ROOT` | `/home` | Root for per-Agent shell HOME directories. Set this to a writable path such as `/tmp/orqivium-agent-home` for local macOS development. |
| `ORQIVIUM_AGENT_STUB_API_BASE_URL` | empty | Public Agent Stub API base URL reachable from shellctl-managed remote machines. HTTP may be the service root or `/agent-stub`; gRPC must be `grpc://host:port`. Enables `ORQIVIUM_AGENT_STUB_*` env injection for user `shell.run` jobs. |
| `ORQIVIUM_AGENT_STUB_GRPC_BIND_ADDRESS` | empty | Optional `host:port` bind override used only when `ORQIVIUM_AGENT_STUB_API_BASE_URL` uses `grpc://`. |
| `ORQIVIUM_AGENT_SERVER_SECRET_KEY` | empty | Security-sensitive server-wide root secret used to derive the JWE encryption key for Agent Stub bearer tokens; required when `ORQIVIUM_AGENT_STUB_API_BASE_URL` is set. The supplied default config uses a development value; set a unique unpadded base64url 32-byte secret in production. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_CONNECT_TIMEOUT` | `10` | Plugin-daemon HTTP connect timeout in seconds. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_READ_TIMEOUT` | `600` | Plugin-daemon HTTP read timeout in seconds. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_WRITE_TIMEOUT` | `30` | Plugin-daemon HTTP write timeout in seconds. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_POOL_TIMEOUT` | `10` | Plugin-daemon HTTP connection-pool wait timeout in seconds. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_MAX_CONNECTIONS` | `100` | Maximum total plugin-daemon HTTP connections. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_MAX_KEEPALIVE_CONNECTIONS` | `20` | Maximum idle keep-alive plugin-daemon HTTP connections. |
| `ORQIVIUM_AGENT_PLUGIN_DAEMON_KEEPALIVE_EXPIRY` | `30` | Keep-alive expiry in seconds for idle plugin-daemon HTTP connections. |

Example `.env`:

```env
ORQIVIUM_AGENT_REDIS_URL=redis://localhost:6379/0
ORQIVIUM_AGENT_REDIS_PREFIX=orqivium-agent-dev
ORQIVIUM_AGENT_SHUTDOWN_GRACE_SECONDS=30
ORQIVIUM_AGENT_RUN_RETENTION_SECONDS=259200
ORQIVIUM_AGENT_PLUGIN_DAEMON_URL=http://localhost:5002
ORQIVIUM_AGENT_PLUGIN_DAEMON_API_KEY=replace-with-daemon-key
ORQIVIUM_AGENT_INNER_API_URL=http://localhost:5001
ORQIVIUM_AGENT_INNER_API_KEY=replace-with-orqivium-inner-api-key-for-plugin
ORQIVIUM_AGENT_SHELLCTL_ENTRYPOINT=http://127.0.0.1:5004
ORQIVIUM_AGENT_SHELLCTL_AUTH_TOKEN=replace-with-shellctl-token
ORQIVIUM_AGENT_SHELL_HOME_ROOT=/tmp/orqivium-agent-home
ORQIVIUM_AGENT_STUB_API_BASE_URL=https://agent.example.com/agent-stub
# This is security-sensitive: it derives the JWE encryption key for Agent Stub bearer tokens.
# Replace this development default in production.
# Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'
ORQIVIUM_AGENT_SERVER_SECRET_KEY=MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY
```

Run records and event streams use the same retention. Status writes refresh the
record TTL, and event writes refresh both the stream TTL and the corresponding
record TTL so active runs that keep producing events remain observable.

## Scheduling and shutdown semantics

`POST /runs` persists a `running` run record and starts an `asyncio` task in the
same process. There is no Redis job stream, consumer group, pending reclaim, or
automatic retry layer. Request-shaped runtime failures such as bad composition,
prompt, output, or snapshot inputs are reported later as failed runs rather than
rejected synchronously once the request DTO itself is accepted.

During FastAPI shutdown the scheduler rejects new runs, waits up to
`ORQIVIUM_AGENT_SHUTDOWN_GRACE_SECONDS` for active tasks, then cancels remaining tasks
and best-effort appends a `run_failed` event plus failed status. A hard process
crash can still leave active runs stuck as `running`; there is no in-service
recovery or worker handoff.

Horizontal scaling is possible by running multiple API processes against the same
Redis prefix, but each process executes only the runs it accepted. Redis provides
shared status/event visibility, not load balancing or queued-job recovery.

## Run inputs and session snapshots

The API does not accept a top-level `user_prompt`. Submit a `RunComposition`
whose Agenton layers provide user input. With the MVP provider set, use
`plain.prompt` and its `config.user` field:

```json
{
  "composition": {
    "schema_version": 1,
    "layers": [
      {
        "name": "prompt",
        "type": "plain.prompt",
        "config": {
          "prefix": "You are concise.",
          "user": "Summarize the current state."
        }
      }
    ]
  }
}
```

`config.user` can be a string or a list of strings. Empty or whitespace-only
effective prompts are rejected during create-run validation before the run is
persisted or scheduled.

There is no Pydantic AI history layer. To resume Agenton layer state, pass the
`session_snapshot` from a previous `run_succeeded.data` payload together with a
composition that has the same layer names and order.

## Observing runs

Use the HTTP status endpoint for coarse state and the event endpoints for detailed
progress:

- `POST /runs` creates a running run and schedules it locally.
- `GET /runs/{run_id}` returns `running`, `succeeded`, or `failed`.
- `GET /runs/{run_id}/events` polls the Redis Stream event log with `after` and
  `next_cursor` cursors.
- `GET /runs/{run_id}/events/sse` replays and streams events over SSE. The SSE
  `id` is the event Redis Stream ID. `after` query cursors take precedence over
  `Last-Event-ID` headers.

Successful runs emit `run_started`, zero or more `pydantic_ai_event`, and
`run_succeeded`. Failed runs end with `run_failed`. Event envelopes retain `id`,
`run_id`, `type`, `data`, and `created_at`; `data` is typed per event type,
including Pydantic AI's `AgentStreamEvent` payload for `pydantic_ai_event` and a
terminal `run_succeeded.data` object containing a `CompositorSessionSnapshot` for
resumption. A successful run has exactly one active result branch: JSON-safe
`output` for final answers, or `deferred_tool_call` when a layer such as
`orqivium.ask_human` ends the current agent run with an external deferred tool call.

## Examples

The repository includes simple consumers that print observed output/events:

- `orqivium-agent/examples/orqivium_agent/orqivium_agent_examples/run_server_consumer.py`
  creates a run and polls events.
- `orqivium-agent/examples/orqivium_agent/orqivium_agent_examples/run_server_sse_consumer.py`
  consumes raw SSE frames for an existing run id.

The create-run examples submit Orqivium plugin model layers, so they require Redis,
the API server, plugin-daemon settings, and provider credentials.
