# Orqivium Enterprise Telemetry Data Dictionary

Quick reference for all telemetry signals emitted by Orqivium Enterprise. For configuration and architecture details, see [README.md](./README.md).

## Resource Attributes

Attached to every signal (Span, Metric, Log).

| Attribute | Type | Example |
|-----------|------|---------|
| `service.name` | string | `orqivium` |
| `host.name` | string | `orqivium-api-7f8b` |

## Traces (Spans)

### `orqivium.workflow.run`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.trace_id` | string | Business trace ID (Workflow Run ID) |
| `orqivium.tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.workflow.id` | string | Workflow definition ID |
| `orqivium.workflow.run_id` | string | Unique ID for this run |
| `orqivium.workflow.status` | string | `succeeded`, `failed`, `stopped`, etc. |
| `orqivium.workflow.error` | string | Error message if failed |
| `orqivium.workflow.elapsed_time` | float | Total execution time (seconds) |
| `orqivium.invoke_from` | string | `api`, `webapp`, `debug` |
| `orqivium.conversation.id` | string | Conversation ID (optional) |
| `orqivium.message.id` | string | Message ID (optional) |
| `orqivium.invoked_by` | string | User ID who triggered the run |
| `gen_ai.usage.total_tokens` | int | Total tokens across all nodes (optional) |
| `gen_ai.user.id` | string | End-user identifier (optional) |
| `orqivium.parent.trace_id` | string | Parent workflow trace ID (optional) |
| `orqivium.parent.workflow.run_id` | string | Parent workflow run ID (optional) |
| `orqivium.parent.node.execution_id` | string | Parent node execution ID (optional) |
| `orqivium.parent.app.id` | string | Parent app ID (optional) |

### `orqivium.node.execution`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.trace_id` | string | Business trace ID |
| `orqivium.tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.workflow.id` | string | Workflow definition ID |
| `orqivium.workflow.run_id` | string | Workflow Run ID |
| `orqivium.message.id` | string | Message ID (optional) |
| `orqivium.conversation.id` | string | Conversation ID (optional) |
| `orqivium.node.execution_id` | string | Unique node execution ID |
| `orqivium.node.id` | string | Node ID in workflow graph |
| `orqivium.node.type` | string | Node type (see appendix) |
| `orqivium.node.title` | string | Display title |
| `orqivium.node.status` | string | `succeeded`, `failed` |
| `orqivium.node.error` | string | Error message if failed |
| `orqivium.node.elapsed_time` | float | Execution time (seconds) |
| `orqivium.node.index` | int | Execution order index |
| `orqivium.node.predecessor_node_id` | string | Triggering node ID |
| `orqivium.node.iteration_id` | string | Iteration ID (optional) |
| `orqivium.node.loop_id` | string | Loop ID (optional) |
| `orqivium.node.parallel_id` | string | Parallel branch ID (optional) |
| `orqivium.node.invoked_by` | string | User ID who triggered execution |
| `gen_ai.usage.input_tokens` | int | Prompt tokens (LLM nodes only) |
| `gen_ai.usage.output_tokens` | int | Completion tokens (LLM nodes only) |
| `gen_ai.usage.total_tokens` | int | Total tokens (LLM nodes only) |
| `gen_ai.request.model` | string | LLM model name (LLM nodes only) |
| `gen_ai.provider.name` | string | LLM provider name (LLM nodes only) |
| `gen_ai.user.id` | string | End-user identifier (optional) |

### `orqivium.node.execution.draft`

Same attributes as `orqivium.node.execution`. Emitted during Preview/Debug runs.

## Counters

All counters are cumulative and emitted at 100% accuracy.

### Token Counters

| Metric | Unit | Description |
|--------|------|-------------|
| `orqivium.tokens.total` | `{token}` | Total tokens consumed |
| `orqivium.tokens.input` | `{token}` | Input (prompt) tokens |
| `orqivium.tokens.output` | `{token}` | Output (completion) tokens |

**Labels:**

- `tenant_id`, `app_id`, `operation_type`, `model_provider`, `model_name`, `node_type` (if node_execution)

⚠️ **Warning:** `orqivium.tokens.total` at workflow level includes all node tokens. Filter by `operation_type` to avoid double-counting.

#### Token Hierarchy & Query Patterns

Token metrics are emitted at multiple layers. Understanding the hierarchy prevents double-counting:

```
App-level total
├── workflow          ← sum of all node_execution tokens (DO NOT add both)
│   └── node_execution ← per-node breakdown
├── message           ← independent (non-workflow chat apps only)
├── rule_generate     ← independent helper LLM call
├── code_generate     ← independent helper LLM call
├── structured_output ← independent helper LLM call
└── instruction_modify← independent helper LLM call
```

**Key rule:** `workflow` tokens already include all `node_execution` tokens. Never sum both.

**Available labels on token metrics:** `tenant_id`, `app_id`, `operation_type`, `model_provider`, `model_name`, `node_type`.
App name is only available on span attributes (`orqivium.app.name`), not metric labels — use `app_id` for metric queries.

**Common queries** (PromQL):

```promql
# ── Totals ──────────────────────────────────────────────────
# App-level total (exclude node_execution to avoid double-counting)
sum by (app_id) (orqivium_tokens_total{operation_type!="node_execution"})

# Single app total
sum (orqivium_tokens_total{app_id="<app_id>", operation_type!="node_execution"})

# Per-tenant totals
sum by (tenant_id) (orqivium_tokens_total{operation_type!="node_execution"})

# ── Drill-down ──────────────────────────────────────────────
# Workflow-level tokens for an app
sum (orqivium_tokens_total{app_id="<app_id>", operation_type="workflow"})

# Node-level breakdown within an app
sum by (node_type) (orqivium_tokens_total{app_id="<app_id>", operation_type="node_execution"})

# Model breakdown for an app
sum by (model_provider, model_name) (orqivium_tokens_total{app_id="<app_id>"})

# Input vs output per model
sum by (model_name) (orqivium_tokens_input_total{app_id="<app_id>"})
sum by (model_name) (orqivium_tokens_output_total{app_id="<app_id>"})

# ── Rates ───────────────────────────────────────────────────
# Token consumption rate (per hour)
sum(rate(orqivium_tokens_total{operation_type!="node_execution"}[1h]))

# Per-app consumption rate
sum by (app_id) (rate(orqivium_tokens_total{operation_type!="node_execution"}[1h]))
```

**Finding `app_id` from app name** (trace query — Tempo / Jaeger):

```
{ resource.orqivium.app.name = "My Chatbot" } | select(resource.orqivium.app.id)
```

### Request Counters

| Metric | Unit | Description |
|--------|------|-------------|
| `orqivium.requests.total` | `{request}` | Total operations count |

**Labels by type:**

| `type` | Additional Labels |
|--------|-------------------|
| `workflow` | `tenant_id`, `app_id`, `status`, `invoke_from` |
| `node` | `tenant_id`, `app_id`, `node_type`, `model_provider`, `model_name`, `status` |
| `draft_node` | `tenant_id`, `app_id`, `node_type`, `model_provider`, `model_name`, `status` |
| `message` | `tenant_id`, `app_id`, `model_provider`, `model_name`, `status`, `invoke_from` |
| `tool` | `tenant_id`, `app_id`, `tool_name` |
| `moderation` | `tenant_id`, `app_id` |
| `suggested_question` | `tenant_id`, `app_id`, `model_provider`, `model_name` |
| `dataset_retrieval` | `tenant_id`, `app_id` |
| `generate_name` | `tenant_id`, `app_id` |
| `prompt_generation` | `tenant_id`, `app_id`, `operation_type`, `model_provider`, `model_name`, `status` |

### Error Counters

| Metric | Unit | Description |
|--------|------|-------------|
| `orqivium.errors.total` | `{error}` | Total failed operations |

**Labels by type:**

| `type` | Additional Labels |
|--------|-------------------|
| `workflow` | `tenant_id`, `app_id` |
| `node` | `tenant_id`, `app_id`, `node_type`, `model_provider`, `model_name` |
| `draft_node` | `tenant_id`, `app_id`, `node_type`, `model_provider`, `model_name` |
| `message` | `tenant_id`, `app_id`, `model_provider`, `model_name` |
| `tool` | `tenant_id`, `app_id`, `tool_name` |
| `prompt_generation` | `tenant_id`, `app_id`, `operation_type`, `model_provider`, `model_name` |

### Other Counters

| Metric | Unit | Labels |
|--------|------|--------|
| `orqivium.feedback.total` | `{feedback}` | `tenant_id`, `app_id`, `rating` |
| `orqivium.dataset.retrievals.total` | `{retrieval}` | `tenant_id`, `app_id`, `dataset_id`, `embedding_model_provider`, `embedding_model`, `rerank_model_provider`, `rerank_model` |
| `orqivium.app.created.total` | `{app}` | `tenant_id`, `app_id`, `mode` |
| `orqivium.app.updated.total` | `{app}` | `tenant_id`, `app_id` |
| `orqivium.app.deleted.total` | `{app}` | `tenant_id`, `app_id` |

## Histograms

| Metric | Unit | Labels |
|--------|------|--------|
| `orqivium.workflow.duration` | `s` | `tenant_id`, `app_id`, `status` |
| `orqivium.node.duration` | `s` | `tenant_id`, `app_id`, `node_type`, `model_provider`, `model_name`, `plugin_name` |
| `orqivium.message.duration` | `s` | `tenant_id`, `app_id`, `model_provider`, `model_name` |
| `orqivium.message.time_to_first_token` | `s` | `tenant_id`, `app_id`, `model_provider`, `model_name` |
| `orqivium.tool.duration` | `s` | `tenant_id`, `app_id`, `tool_name` |
| `orqivium.prompt_generation.duration` | `s` | `tenant_id`, `app_id`, `operation_type`, `model_provider`, `model_name` |

## Structured Logs

### Span Companion Logs

Logs that accompany spans. Signal type: `span_detail`

#### `orqivium.workflow.run` Companion Log

**Common attributes:** All span attributes (see Traces section) plus:

| Additional Attribute | Type | Always Present | Description |
|---------------------|------|----------------|-------------|
| `orqivium.app.name` | string | No | Application display name |
| `orqivium.workspace.name` | string | No | Workspace display name |
| `orqivium.workflow.version` | string | Yes | Workflow definition version |
| `orqivium.workflow.inputs` | string/JSON | Yes | Input parameters (content-gated) |
| `orqivium.workflow.outputs` | string/JSON | Yes | Output results (content-gated) |
| `orqivium.workflow.query` | string | No | User query text (content-gated) |

**Event attributes:**

- `orqivium.event.name`: `"orqivium.workflow.run"`
- `orqivium.event.signal`: `"span_detail"`
- `trace_id`, `span_id`, `tenant_id`, `user_id`

#### `orqivium.node.execution` and `orqivium.node.execution.draft` Companion Logs

**Common attributes:** All span attributes (see Traces section) plus:

| Additional Attribute | Type | Always Present | Description |
|---------------------|------|----------------|-------------|
| `orqivium.app.name` | string | No | Application display name |
| `orqivium.workspace.name` | string | No | Workspace display name |
| `orqivium.invoke_from` | string | No | Invocation source |
| `gen_ai.tool.name` | string | No | Tool name (tool nodes only) |
| `orqivium.node.total_price` | float | No | Cost (LLM nodes only) |
| `orqivium.node.currency` | string | No | Currency code (LLM nodes only) |
| `orqivium.node.iteration_index` | int | No | Iteration index (iteration nodes) |
| `orqivium.node.loop_index` | int | No | Loop index (loop nodes) |
| `orqivium.plugin.name` | string | No | Plugin name (tool/knowledge nodes) |
| `orqivium.credential.name` | string | No | Credential name (plugin nodes) |
| `orqivium.credential.id` | string | No | Credential ID (plugin nodes) |
| `orqivium.dataset.ids` | JSON array | No | Dataset IDs (knowledge nodes) |
| `orqivium.dataset.names` | JSON array | No | Dataset names (knowledge nodes) |
| `orqivium.node.inputs` | string/JSON | Yes | Node inputs (content-gated) |
| `orqivium.node.outputs` | string/JSON | Yes | Node outputs (content-gated) |
| `orqivium.node.process_data` | string/JSON | No | Processing data (content-gated) |

**Event attributes:**

- `orqivium.event.name`: `"orqivium.node.execution"` or `"orqivium.node.execution.draft"`
- `orqivium.event.signal`: `"span_detail"`
- `trace_id`, `span_id`, `tenant_id`, `user_id`

### Standalone Logs

Logs without structural spans. Signal type: `metric_only`

#### `orqivium.message.run`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.message.run"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID (32-char hex) |
| `span_id` | string | OTEL span ID (16-char hex) |
| `tenant_id` | string | Tenant identifier |
| `user_id` | string | User identifier (optional) |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.message.id` | string | Message identifier |
| `orqivium.conversation.id` | string | Conversation ID (optional) |
| `orqivium.workflow.run_id` | string | Workflow run ID (optional) |
| `orqivium.invoke_from` | string | `service-api`, `web-app`, `debugger`, `explore` |
| `gen_ai.provider.name` | string | LLM provider |
| `gen_ai.request.model` | string | LLM model |
| `gen_ai.usage.input_tokens` | int | Input tokens |
| `gen_ai.usage.output_tokens` | int | Output tokens |
| `gen_ai.usage.total_tokens` | int | Total tokens |
| `orqivium.message.status` | string | `succeeded`, `failed` |
| `orqivium.message.error` | string | Error message (if failed) |
| `orqivium.message.duration` | float | Duration (seconds) |
| `orqivium.message.time_to_first_token` | float | TTFT (seconds) |
| `orqivium.message.inputs` | string/JSON | Inputs (content-gated) |
| `orqivium.message.outputs` | string/JSON | Outputs (content-gated) |

#### `orqivium.tool.execution`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.tool.execution"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID |
| `span_id` | string | OTEL span ID |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.message.id` | string | Message identifier |
| `orqivium.tool.name` | string | Tool name |
| `orqivium.tool.duration` | float | Duration (seconds) |
| `orqivium.tool.status` | string | `succeeded`, `failed` |
| `orqivium.tool.error` | string | Error message (if failed) |
| `orqivium.tool.inputs` | string/JSON | Inputs (content-gated) |
| `orqivium.tool.outputs` | string/JSON | Outputs (content-gated) |
| `orqivium.tool.parameters` | string/JSON | Parameters (content-gated) |
| `orqivium.tool.config` | string/JSON | Configuration (content-gated) |

#### `orqivium.moderation.check`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.moderation.check"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID |
| `span_id` | string | OTEL span ID |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.message.id` | string | Message identifier |
| `orqivium.moderation.type` | string | `input`, `output` |
| `orqivium.moderation.action` | string | `pass`, `block`, `flag` |
| `orqivium.moderation.flagged` | boolean | Whether flagged |
| `orqivium.moderation.categories` | JSON array | Flagged categories |
| `orqivium.moderation.query` | string | Content (content-gated) |

#### `orqivium.suggested_question.generation`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.suggested_question.generation"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID |
| `span_id` | string | OTEL span ID |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.message.id` | string | Message identifier |
| `orqivium.suggested_question.count` | int | Number of questions |
| `orqivium.suggested_question.duration` | float | Duration (seconds) |
| `orqivium.suggested_question.status` | string | `succeeded`, `failed` |
| `orqivium.suggested_question.error` | string | Error message (if failed) |
| `orqivium.suggested_question.questions` | JSON array | Questions (content-gated) |

#### `orqivium.dataset.retrieval`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.dataset.retrieval"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID |
| `span_id` | string | OTEL span ID |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.message.id` | string | Message identifier |
| `orqivium.dataset.id` | string | Dataset identifier |
| `orqivium.dataset.name` | string | Dataset name |
| `orqivium.dataset.embedding_providers` | JSON array | Embedding model providers (one per dataset) |
| `orqivium.dataset.embedding_models` | JSON array | Embedding models (one per dataset) |
| `orqivium.retrieval.rerank_provider` | string | Rerank model provider |
| `orqivium.retrieval.rerank_model` | string | Rerank model name |
| `orqivium.retrieval.query` | string | Search query (content-gated) |
| `orqivium.retrieval.document_count` | int | Documents retrieved |
| `orqivium.retrieval.duration` | float | Duration (seconds) |
| `orqivium.retrieval.status` | string | `succeeded`, `failed` |
| `orqivium.retrieval.error` | string | Error message (if failed) |
| `orqivium.dataset.documents` | JSON array | Documents (content-gated) |

#### `orqivium.generate_name.execution`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.generate_name.execution"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID |
| `span_id` | string | OTEL span ID |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.conversation.id` | string | Conversation identifier |
| `orqivium.generate_name.duration` | float | Duration (seconds) |
| `orqivium.generate_name.status` | string | `succeeded`, `failed` |
| `orqivium.generate_name.error` | string | Error message (if failed) |
| `orqivium.generate_name.inputs` | string/JSON | Inputs (content-gated) |
| `orqivium.generate_name.outputs` | string | Generated name (content-gated) |

#### `orqivium.prompt_generation.execution`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.prompt_generation.execution"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID |
| `span_id` | string | OTEL span ID |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.prompt_generation.operation_type` | string | Operation type (see appendix) |
| `gen_ai.provider.name` | string | LLM provider |
| `gen_ai.request.model` | string | LLM model |
| `gen_ai.usage.input_tokens` | int | Input tokens |
| `gen_ai.usage.output_tokens` | int | Output tokens |
| `gen_ai.usage.total_tokens` | int | Total tokens |
| `orqivium.prompt_generation.duration` | float | Duration (seconds) |
| `orqivium.prompt_generation.status` | string | `succeeded`, `failed` |
| `orqivium.prompt_generation.error` | string | Error message (if failed) |
| `orqivium.prompt_generation.instruction` | string | Instruction (content-gated) |
| `orqivium.prompt_generation.output` | string/JSON | Output (content-gated) |

#### `orqivium.app.created`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.app.created"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.app.mode` | string | `chat`, `completion`, `agent-chat`, `workflow` |
| `orqivium.app.created_at` | string | Timestamp (ISO 8601) |

#### `orqivium.app.updated`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.app.updated"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.app.updated_at` | string | Timestamp (ISO 8601) |

#### `orqivium.app.deleted`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.app.deleted"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.app.deleted_at` | string | Timestamp (ISO 8601) |

#### `orqivium.feedback.created`

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.feedback.created"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `trace_id` | string | OTEL trace ID |
| `span_id` | string | OTEL span ID |
| `tenant_id` | string | Tenant identifier |
| `orqivium.app_id` | string | Application identifier |
| `orqivium.message.id` | string | Message identifier |
| `orqivium.feedback.rating` | string | `like`, `dislike`, `null` |
| `orqivium.feedback.content` | string | Feedback text (content-gated) |
| `orqivium.feedback.created_at` | string | Timestamp (ISO 8601) |

#### `orqivium.telemetry.rehydration_failed`

Diagnostic event for telemetry system health monitoring.

| Attribute | Type | Description |
|-----------|------|-------------|
| `orqivium.event.name` | string | `"orqivium.telemetry.rehydration_failed"` |
| `orqivium.event.signal` | string | `"metric_only"` |
| `tenant_id` | string | Tenant identifier |
| `orqivium.telemetry.error` | string | Error message |
| `orqivium.telemetry.payload_type` | string | Payload type (see appendix) |
| `orqivium.telemetry.correlation_id` | string | Correlation ID |

## Content-Gated Attributes

When `ENTERPRISE_INCLUDE_CONTENT=false`, these attributes are replaced with reference strings (`ref:{id_type}={uuid}`).

| Attribute | Signal |
|-----------|--------|
| `orqivium.workflow.inputs` | `orqivium.workflow.run` |
| `orqivium.workflow.outputs` | `orqivium.workflow.run` |
| `orqivium.workflow.query` | `orqivium.workflow.run` |
| `orqivium.node.inputs` | `orqivium.node.execution` |
| `orqivium.node.outputs` | `orqivium.node.execution` |
| `orqivium.node.process_data` | `orqivium.node.execution` |
| `orqivium.message.inputs` | `orqivium.message.run` |
| `orqivium.message.outputs` | `orqivium.message.run` |
| `orqivium.tool.inputs` | `orqivium.tool.execution` |
| `orqivium.tool.outputs` | `orqivium.tool.execution` |
| `orqivium.tool.parameters` | `orqivium.tool.execution` |
| `orqivium.tool.config` | `orqivium.tool.execution` |
| `orqivium.moderation.query` | `orqivium.moderation.check` |
| `orqivium.suggested_question.questions` | `orqivium.suggested_question.generation` |
| `orqivium.retrieval.query` | `orqivium.dataset.retrieval` |
| `orqivium.dataset.documents` | `orqivium.dataset.retrieval` |
| `orqivium.generate_name.inputs` | `orqivium.generate_name.execution` |
| `orqivium.generate_name.outputs` | `orqivium.generate_name.execution` |
| `orqivium.prompt_generation.instruction` | `orqivium.prompt_generation.execution` |
| `orqivium.prompt_generation.output` | `orqivium.prompt_generation.execution` |
| `orqivium.feedback.content` | `orqivium.feedback.created` |

## Appendix

### Operation Types

- `workflow`, `node_execution`, `message`, `rule_generate`, `code_generate`, `structured_output`, `instruction_modify`

### Node Types

- `start`, `end`, `answer`, `llm`, `knowledge-retrieval`, `knowledge-index`, `if-else`, `code`, `template-transform`, `question-classifier`, `http-request`, `tool`, `datasource`, `variable-aggregator`, `loop`, `iteration`, `parameter-extractor`, `assigner`, `document-extractor`, `list-operator`, `agent`, `trigger-webhook`, `trigger-schedule`, `trigger-plugin`, `human-input`

### Workflow Statuses

- `running`, `succeeded`, `failed`, `stopped`, `partial-succeeded`, `paused`

### Payload Types

- `workflow`, `node`, `message`, `tool`, `moderation`, `suggested_question`, `dataset_retrieval`, `generate_name`, `prompt_generation`, `app`, `feedback`

### Null Value Behavior

**Spans:** Attributes with `null` values are omitted.

**Logs:** Attributes with `null` values appear as `null` in JSON.

**Content-Gated:** Replaced with reference strings, not set to `null`.
