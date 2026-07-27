# Orqivium System Architecture

Orqivium is a production-oriented platform for engineering, governing, and operating agentic AI workflows, built and maintained by **Kamran Ullah Afaq**. It combines a mature distributed execution model with a publication-time governance control plane, deterministic workflow identity, and an evidence-centered operating model.

## 1. System context

```mermaid
flowchart LR
    Builder[Workflow Builder / Operator]
    EndUser[Application End User]
    Admin[Platform Administrator]
    Orqivium[Orqivium]
    Models[Model Providers]
    Tools[Tools, MCP Servers, APIs]
    Data[Documents, Object Storage, Vector Stores]
    Obs[OpenTelemetry, Sentry, Trace Backends]

    Builder -->|design, test, publish| Orqivium
    EndUser -->|chat, API, workflow run| Orqivium
    Admin -->|policy, credentials, deployment| Orqivium
    Orqivium -->|inference and embeddings| Models
    Orqivium -->|tool calls and actions| Tools
    Orqivium -->|ingest, retrieve, persist| Data
    Orqivium -->|traces, logs, metrics| Obs
```

## 2. Container architecture

```mermaid
flowchart TB
    subgraph Client
      Web[Next.js Web Console]
      SDK[REST / SDK / CLI Clients]
    end

    subgraph ControlPlane[Application and Control Plane]
      API[Flask API]
      Gov[Governance Analyzer]
      Auth[Auth, RBAC, Credentials]
      Publish[Draft and Publish Services]
      Plugin[Plugin / MCP Integration]
    end

    subgraph ExecutionPlane[Execution Plane]
      Graph[Graphon Workflow Runtime]
      Worker[Celery Workers]
      Beat[Celery Beat]
      Agent[Agent Backend]
      Sandbox[Code Sandbox]
    end

    subgraph State
      PG[(PostgreSQL)]
      Redis[(Redis)]
      Object[(Object Storage)]
      VDB[(Vector Database)]
    end

    subgraph External
      LLM[LLM / Embedding / Rerank Providers]
      APIs[External APIs and Tools]
      Telemetry[OTel / Sentry / Trace Providers]
    end

    Web --> API
    SDK --> API
    API --> Auth
    API --> Publish
    Publish --> Gov
    Publish --> PG
    API --> Graph
    Graph --> Worker
    Worker --> Redis
    Beat --> Worker
    Worker --> Agent
    Worker --> Sandbox
    Graph --> PG
    Graph --> Object
    Graph --> VDB
    Graph --> LLM
    Graph --> APIs
    API --> Telemetry
    Worker --> Telemetry
    Agent --> Telemetry
    Plugin --> APIs
```

## 3. Workflow lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Validated: structural validation
    Validated --> Audited: governance analysis + fingerprint
    Audited --> Draft: findings require changes
    Audited --> Published: policy passes
    Published --> Running: user/API/trigger invocation
    Running --> Paused: human input required
    Paused --> Running: approved/resumed
    Running --> Succeeded
    Running --> Failed
    Running --> Stopped
    Succeeded --> Observed
    Failed --> Observed
    Stopped --> Observed
    Observed --> Draft: improve using traces and evals
```

## 4. Publication sequence

```mermaid
sequenceDiagram
    actor Builder
    participant Web as Web Console
    participant API as Flask API
    participant Service as WorkflowService
    participant Gov as Orqivium Governance
    participant DB as PostgreSQL
    participant Events as Event Bus / Handlers

    Builder->>Web: Publish draft
    Web->>API: POST publish
    API->>Service: publish_workflow(...)
    Service->>Service: credential and graph validation
    Service->>Gov: audit_for_publication(graph, policy)
    Gov->>Gov: canonicalize runtime semantics
    Gov->>Gov: compute SHA-256 fingerprint
    Gov->>Gov: risk, agency, security, bounds analysis
    alt policy blocked
      Gov-->>Service: WorkflowGovernanceViolationError
      Service-->>API: actionable validation error
      API-->>Web: publication rejected
    else policy passed
      Gov-->>Service: audit report
      Service->>DB: create immutable published snapshot
      Service->>Events: published workflow updated
      Service-->>API: published workflow
      API-->>Web: success
    end
```

## 5. RAG and agent action boundary

```mermaid
flowchart LR
    Input[User / Trigger Input]
    Retrieve[Knowledge Retrieval]
    Normalize[Content Normalization]
    Model[LLM / Agent Reasoning]
    Validate[Structured Output and Policy Validation]
    Approve{Human Approval Required?}
    Human[Human Input Gate]
    Action[Tool / HTTP / MCP Action]
    Result[Result + Trace + Evaluation]

    Input --> Retrieve --> Normalize --> Model --> Validate --> Approve
    Approve -->|yes| Human --> Action
    Approve -->|no, read-only| Action
    Action --> Result

    Untrusted[Untrusted retrieved instructions] -. prompt injection risk .-> Model
    Validate -. reject unsafe arguments .-> Result
```

## 6. Reliability model

The platform applies layered reliability rather than assuming model correctness:

- deterministic graph and credential validation;
- semantic fingerprinting for version identity;
- bounded execution time, agent iteration, and loop limits;
- Redis-backed command and asynchronous coordination;
- immutable published snapshots;
- human-in-the-loop pause and resume;
- trace propagation through API and worker boundaries;
- sandboxed code execution;
- policy profiles matched to deployment risk.

## 7. Data ownership and tenancy

PostgreSQL stores application metadata, workflow versions, runs, messages, credentials references, datasets, and operational state. Object storage holds uploaded and generated files. Redis supports caching, queues, pub/sub, locks, and stop commands. Vector stores hold retrieval indexes. Tenant and workspace identifiers are carried through service and repository boundaries.

## 8. Extension points

- model providers and model load balancing;
- vector database provider packages;
- trace provider packages;
- built-in, custom, plugin, MCP, and workflow-as-tool integrations;
- datasource ingestion plugins;
- trigger nodes;
- CLI and SDK clients;
- OpenTelemetry exporters and external evaluation systems.
