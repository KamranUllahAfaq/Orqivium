# Threat Model

## Assets

- tenant data and uploaded documents;
- model, tool, OAuth, and storage credentials;
- workflow definitions and prompts;
- generated files and conversation history;
- billing capacity and model quotas;
- administrative and publication permissions;
- execution traces that may contain sensitive content.

## Trust boundaries

1. browser to API;
2. API to database, Redis, and object storage;
3. workflow runtime to model providers;
4. workflow runtime to tools, MCP servers, and external APIs;
5. API/worker to plugin daemon and agent backend;
6. workflow runtime to code sandbox;
7. retrieval pipeline to untrusted documents and web content;
8. telemetry pipeline to external observability providers.

## Priority threats and controls

| Threat | Example | Primary controls |
|---|---|---|
| Prompt injection | document tells an agent to ignore policy and call a tool | isolate data/instructions, argument validation, human approval, least-privilege tools |
| Sensitive data disclosure | prompt or trace includes secrets or private records | credential references, secret scanning, redaction, data minimization, trace-content opt-in |
| Excessive agency | agent sends, deletes, pays, or deploys autonomously | explicit action scopes, human approval, policy profiles, immutable audit trail |
| Unbounded consumption | loops or agents consume tokens indefinitely | iteration limits, execution timeout, rate limits, budgets, queue isolation |
| SSRF and network abuse | HTTP node reaches internal metadata service | SSRF proxy, destination policy, egress allowlists, DNS/IP validation |
| Unsafe code execution | generated code escapes or exhausts sandbox | isolated sandbox, no host mounts, resource quotas, timeouts, output bounds |
| Supply-chain compromise | malicious plugin/model package | signed artifacts, pinned versions, provenance review, isolated plugin execution |
| Cross-tenant access | object or record queried under wrong workspace | tenant-scoped repositories, authorization checks, negative tests, audit logs |
| Replay and duplicate actions | webhook retried and charges twice | signatures, timestamps, replay cache, idempotency keys |
| Observability leakage | prompts and tool results exported externally | content capture off by default, redaction, retention rules, provider review |

## Residual risk

Static analysis cannot know every external tool's real permissions, whether a model provider retains content, or whether a human approval is meaningful. Deployment owners must combine governance findings with runtime authorization, provider contracts, network controls, evals, and incident response.
