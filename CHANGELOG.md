# Orqivium Changelog

## 2.0.0 — 2026-07-27

### Product identity

- Established the Orqivium name, positioning, visual system, logo, favicon, terms, privacy, and product documentation.
- Identified Kamran Ullah Afaq as builder and maintainer of Orqivium-specific work.
- Migrated product-facing strings, package names, service names, environment variables, repository metadata, examples, tests, and documentation routes.
- Renamed the agent package and runtime to `orqivium-agent` and `orqivium-agent-runtime`.
- Renamed the CLI to `orqctl`, the SDK surfaces to Orqivium, and the design-system package to `orqivium-ui`.
- Isolated required legal and source-provenance records under `legal/`.

### Architecture and governance

- Added deterministic semantic workflow fingerprints.
- Added deterministic audit IDs, policy fingerprints, analyzer versions, schema versions, and policy revisions.
- Added graph integrity, cycle, reachability, termination, resource, secret, action-authority, webhook, and retrieval-to-action analysis.
- Added configurable publication policy profiles and risk thresholds.
- Integrated governance into application, snippet, and knowledge-pipeline publication paths before immutable snapshots are created.
- Added JSON and Markdown evidence outputs and a versioned report schema.

### Deployment and operations

- Added Orqivium image variables and local build definitions for the API, web application, agent backend, and agent sandbox.
- Replaced example database, Redis, certificate, and service identities with Orqivium defaults.
- Added explicit configuration for separately distributed code-sandbox and plugin-daemon images.
- Updated repository automation, test configuration, observability labels, and release metadata.

### Documentation and quality

- Rebuilt the README as a product-grade technical entry point.
- Added complete component, lifecycle, flow, threat, evaluation, and research documentation.
- Added safe and intentionally high-risk reproducible governance examples.
- Added release validation, inventory, integrity, and packaging checks.
