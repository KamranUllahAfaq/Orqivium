# Research Rationale for the Orqivium Improvements

The improved architecture focuses on the gap between **workflow validity** and **workflow trustworthiness**.

A visual agent workflow can be valid yet still fail in production because it has unreachable paths, implicit termination, unbounded model/tool loops, secret-bearing configuration, retrieval-to-action prompt-injection exposure, or no human checkpoint before irreversible actions. The new control plane therefore uses deterministic static analysis before publication, not another language model, to avoid circular dependence on probabilistic judgment.

The design is informed by four principles:

1. **Risk must be governed across the lifecycle.** Publication is treated as a formal transition from mutable design to immutable deployable artifact.
2. **Agent output is untrusted at action boundaries.** Model output and retrieved content must be validated before tools execute side effects.
3. **Evals are a first-class engineering discipline.** Nondeterministic behavior requires representative test sets, trace-derived cases, and measurable acceptance criteria.
4. **Observability needs shared semantics.** Workflow, model, retrieval, tool, token, latency, and evaluation signals should be correlated through standard trace context.

Primary references:

- NIST AI Risk Management Framework 1.0 and the Generative AI Profile (NIST AI 600-1).
- OWASP Top 10 for LLM Applications 2025 and Top 10 for Agentic Applications 2026.
- OpenTelemetry Generative AI semantic conventions.
- OpenAI guidance on agent design, evaluations, and trace-driven improvement loops.

## Primary-source links

- NIST AI RMF Generative AI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- OWASP Top 10 for LLM and GenAI Applications 2025: https://genai.owasp.org/llm-top-10/
- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- OpenTelemetry Generative AI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenAI practical guide to building agents: https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- OpenAI evaluation guide: https://developers.openai.com/api/docs/guides/evals
