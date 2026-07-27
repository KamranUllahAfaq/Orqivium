# End-to-End Flow Catalog

This document maps the principal Orqivium flows, their state transitions, trust boundaries, and failure behavior.

## 1. Draft authoring and save

```mermaid
sequenceDiagram
    actor Builder
    participant Web
    participant API
    participant Service
    participant DB as PostgreSQL

    Builder->>Web: edit graph, variables, model/tool settings
    Web->>API: save draft
    API->>Service: validate request and tenant scope
    Service->>DB: create/update draft workflow
    DB-->>Service: persisted draft
    Service-->>Web: draft version/hash
```

**Invariants:** tenant-scoped access; one mutable draft per app/workflow kind; graph JSON remains parseable; credential values should be referenced, not embedded.

## 2. Debug execution

```mermaid
flowchart LR
    UI[Debug request] --> API[API config assembly]
    API --> Graph[Graphon runtime]
    Graph --> Vars[Variable pool]
    Graph --> Nodes[Node execution]
    Nodes --> Models[Models]
    Nodes --> Tools[Tools / HTTP / MCP]
    Nodes --> Data[RAG / files / storage]
    Nodes --> Events[streamed node and graph events]
    Events --> UI
    Events --> State[(execution traces/state)]
```

**Failure behavior:** node failure strategy may fail, continue, or route to error handling; stop commands and timeouts terminate runs; debug execution never replaces publication validation.

## 3. Publication and governance

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> NativeValidated
    NativeValidated --> Governed: fingerprint + findings + risk
    Governed --> Draft: blocked
    Governed --> Published: policy passes
    Published --> [*]
```

**Ordering:** credential validation → native graph validation → agent binding validation → Orqivium audit → billing/plan rules where applicable → immutable snapshot.

**Atomicity objective:** no published snapshot should be created after a governance rejection.

## 4. Synchronous application invocation

```mermaid
sequenceDiagram
    actor Client
    participant API
    participant Config as App Config Manager
    participant Runtime as Workflow Runtime
    participant Provider as Model/Tool/Data Provider
    participant DB

    Client->>API: invoke app
    API->>Config: resolve published app and features
    Config->>DB: load published workflow and variables
    Config-->>API: executable configuration
    API->>Runtime: start run
    Runtime->>Provider: model/retrieval/tool calls
    Provider-->>Runtime: outputs
    Runtime->>DB: run/node state and usage
    Runtime-->>API: stream/events/result
    API-->>Client: response
```

## 5. Triggered and asynchronous execution

```mermaid
flowchart LR
    Trigger[Webhook / schedule / plugin] --> Verify[auth, schema, replay/rate checks]
    Verify --> Queue[(Redis/Celery)]
    Queue --> Worker[Worker]
    Worker --> Runtime[Workflow runtime]
    Runtime --> State[(PostgreSQL)]
    Runtime --> External[models/tools/data]
    Runtime --> Notify[event/notification delivery]
```

**Required controls:** authenticated triggers, replay prevention, idempotency for actions, queue isolation, retries with bounded backoff, and dead-letter/operational review procedures.

## 6. Human-in-the-loop pause and resume

```mermaid
sequenceDiagram
    participant Runtime
    participant DB
    participant Delivery as Email/Web/API Delivery
    actor Reviewer

    Runtime->>DB: persist paused execution and form
    Runtime->>Delivery: deliver approval/input request
    Delivery->>Reviewer: render exact action/context
    Reviewer->>Delivery: approve, reject, or provide values
    Delivery->>DB: validate recipient/token/state
    DB-->>Runtime: resume command and approved payload
    Runtime->>Runtime: continue from paused node
```

**High-assurance requirement:** approval should bind to a normalized hash of the exact external action payload, actor, policy, and expiry so parameters cannot change after approval.

## 7. RAG ingestion

```mermaid
flowchart LR
    Source[files / drive / website / datasource] --> Extract[extract and normalize]
    Extract --> Split[chunk and metadata]
    Split --> Embed[embedding provider]
    Embed --> Index[(vector store)]
    Split --> Meta[(PostgreSQL/object storage)]
    Index --> Status[indexing state and diagnostics]
```

**Quality controls:** source provenance, parser failure visibility, deterministic chunking configuration, duplicate detection, embedding-model identity, index version, and deletion consistency.

## 8. RAG retrieval and generation

```mermaid
flowchart LR
    Query --> Rewrite[optional query transform]
    Rewrite --> Retrieve[hybrid/vector retrieval]
    Retrieve --> Rerank[optional reranker]
    Rerank --> Context[context assembly]
    Context --> Model[LLM]
    Model --> Ground[grounding/citation validation]
    Ground --> Response
```

Retrieved content is untrusted data. It must not automatically become privileged instructions, especially when downstream nodes can perform side effects.

## 9. Agent/tool loop

```mermaid
stateDiagram-v2
    [*] --> Reason
    Reason --> ValidateArgs: propose tool call
    ValidateArgs --> Approve: high-impact action
    ValidateArgs --> Execute: read-only/low-risk action
    Approve --> Execute: approved
    Approve --> Stop: rejected/expired
    Execute --> Observe
    Observe --> Reason: more work within bound
    Observe --> Complete: task done
    Reason --> Stop: iteration/time/token budget reached
```

**Controls:** explicit tool scopes; structured schemas; output validation; iteration, token, time, and cost bounds; human approval; idempotency; safe retry semantics.

## 10. Code node execution

```mermaid
flowchart LR
    Runtime --> Request[code + declared inputs]
    Request --> Sandbox[isolated sandbox]
    Sandbox --> Limits[CPU/memory/time/output/network limits]
    Limits --> Result[validated output or failure]
    Result --> Runtime
```

The sandbox should have no host mounts, no ambient cloud credentials, restricted egress, pinned runtime images, and strict output size limits.

## 11. Plugin and MCP boundary

```mermaid
flowchart LR
    Workflow --> Adapter[plugin/MCP adapter]
    Adapter --> Credential[scoped credential reference]
    Adapter --> Remote[plugin daemon / MCP server]
    Remote --> System[external system]
    System --> Remote --> Validate[response validation] --> Workflow
```

Third-party descriptors should eventually declare operation semantics, data handling, risk class, version, and provenance.

## 12. Observability and evaluation

```mermaid
flowchart LR
    API[API spans/logs] --> Correlate[trace + tenant/app/workflow/fingerprint]
    Worker[worker spans/logs] --> Correlate
    Model[model usage/latency] --> Correlate
    Retrieve[retrieval documents/scores] --> Correlate
    Tool[tool calls/results] --> Correlate
    Correlate --> Store[trace backend]
    Store --> Cases[representative eval cases]
    Cases --> Eval[offline/online evaluation]
    Eval --> Gate[thresholds and regression decisions]
    Gate --> Improve[workflow revision]
```

Telemetry content can itself be sensitive. Capture prompts, retrieved documents, tool arguments, and outputs only under explicit policy with redaction and retention controls.
