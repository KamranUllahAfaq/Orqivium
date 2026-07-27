# ADR-001: Publication-Time Governance Control Plane

- **Status:** Accepted
- **Owner:** Kamran Ullah Afaq
- **Project:** Orqivium
- **Decision date:** 2026-07-27

## Context

Agentic workflows combine nondeterministic model outputs, retrieved untrusted content, executable tools, external APIs, code sandboxes, and asynchronous state. Traditional schema validation confirms that a graph is syntactically valid, but it does not answer whether the graph is reproducible, bounded, observable, or safe to publish.

## Decision

Orqivium adds a deterministic governance gate immediately before a draft workflow is copied into an immutable published snapshot. The gate computes a semantic fingerprint and evaluates:

1. graph integrity and reachability;
2. bounded loops and agent iterations;
3. plaintext secret exposure;
4. high-impact tool and HTTP actions;
5. human approval boundaries;
6. indirect prompt-injection paths from retrieval to actions;
7. webhook-to-side-effect paths;
8. nondeterministic model settings on action paths.

Four policy profiles are supported: `off`, `advisory`, `standard`, and `high_assurance`. Advisory is the compatibility-preserving default.

## Why publication time

- The graph is complete enough to analyze.
- The user still has an opportunity to correct findings.
- Runtime execution remains unchanged.
- Every published snapshot receives a stable semantic identity.
- A rejected publication cannot create a partially deployed version.

## Consequences

### Positive

- Stronger auditability and reproducibility.
- Earlier detection of broken or unsafe paths.
- Explicit policy profiles for different risk tolerances.
- No model call is required for the audit.
- Existing workflows continue to publish under advisory mode.

### Trade-offs

- Static analysis cannot fully infer third-party tool semantics.
- High-assurance mode can require workflow redesign.
- Semantic fingerprints intentionally ignore editor-only layout changes.
- Governance complements, rather than replaces, runtime authorization and sandboxing.
