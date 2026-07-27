from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .fingerprint import semantic_workflow_fingerprint
from .models import FindingSeverity, GovernanceMode, RiskLevel, WorkflowAuditReport, WorkflowFinding

_ENTRY_TYPES = {
    "start",
    "trigger-webhook",
    "trigger-schedule",
    "trigger-plugin",
    "webhook-trigger",
    "schedule-trigger",
    "plugin-trigger",
    "datasource",
}
_TERMINAL_TYPES = {"end", "answer", "knowledge-index"}
_HUMAN_TYPES = {"human-input", "human_input"}
_LOOP_TYPES = {"loop", "iteration"}
_RETRIEVAL_TYPES = {"knowledge-retrieval", "knowledge_retrieval"}
_AGENT_TYPES = {"agent", "agent-v2", "agent_v2"}
_CODE_TYPES = {"code"}
_HTTP_TYPES = {"http-request", "http_request"}
_TOOL_TYPES = {"tool", "mcp-tool", "mcp_tool", "workflow-tool", "workflow_tool"}

_MUTATING_HTTP_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_ACTION_KEYWORDS = {
    "approve",
    "archive",
    "cancel",
    "create",
    "delete",
    "deploy",
    "execute",
    "forward",
    "issue",
    "message",
    "pay",
    "payment",
    "post",
    "publish",
    "refund",
    "remove",
    "send",
    "submit",
    "transfer",
    "trash",
    "update",
    "upload",
    "write",
}
_SENSITIVE_KEYS = {
    "access_token",
    "api_key",
    "client_secret",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "secret_key",
}
_SEVERITY_WEIGHT = {
    FindingSeverity.INFO: 0,
    FindingSeverity.LOW: 2,
    FindingSeverity.MEDIUM: 7,
    FindingSeverity.HIGH: 15,
    FindingSeverity.CRITICAL: 25,
}
_STANDARD_STRUCTURAL_BLOCKERS = {
    "graph.empty",
    "graph.node.invalid",
    "graph.edge.invalid",
    "graph.edge.missing_endpoint",
    "graph.edge.dangling",
    "graph.path.no_terminal",
    "graph.cycle.unbounded",
}


@dataclass(frozen=True, slots=True)
class _Node:
    node_id: str
    node_type: str
    raw: Mapping[str, Any]
    data: Mapping[str, Any]
    nested: bool


@dataclass(frozen=True, slots=True)
class _Edge:
    source: str
    target: str
    raw: Mapping[str, Any]


def _node_type(node: Mapping[str, Any]) -> str:
    data = node.get("data")
    if isinstance(data, Mapping):
        value = data.get("type")
        if isinstance(value, str) and value:
            return value.lower()
    value = node.get("type")
    return value.lower() if isinstance(value, str) and value else "unknown"


def _node_data(node: Mapping[str, Any]) -> Mapping[str, Any]:
    data = node.get("data")
    return data if isinstance(data, Mapping) else {}


def _is_nested(node: Mapping[str, Any], data: Mapping[str, Any]) -> bool:
    parent_candidates = (
        node.get("parentId"),
        node.get("parent_id"),
        data.get("parentId"),
        data.get("parent_id"),
        data.get("iteration_id"),
        data.get("loop_id"),
    )
    return any(isinstance(value, str) and value for value in parent_candidates) or bool(
        data.get("isInIteration") or data.get("isInLoop")
    )


def _iter_sensitive_values(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = (*path, str(key))
            normalized_key = str(key).lower()
            if normalized_key in _SENSITIVE_KEYS and isinstance(child, str):
                stripped = child.strip()
                if (
                    len(stripped) >= 8
                    and not stripped.startswith(("${", "{{", "env.", "secret://", "vault://"))
                    and not stripped.endswith(("_id", "-id"))
                ):
                    yield child_path, stripped
            yield from _iter_sensitive_values(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _iter_sensitive_values(child, (*path, str(index)))


def _extract_http_method(data: Mapping[str, Any]) -> str | None:
    for key in ("method", "http_method", "request_method"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value.upper()
    return None


def _flatten_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, Mapping):
        for child in value.values():
            strings.extend(_flatten_strings(child))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            strings.extend(_flatten_strings(child))
    return strings


def _tool_looks_mutating(data: Mapping[str, Any]) -> bool:
    inspected = {
        "tool_name": data.get("tool_name"),
        "provider_id": data.get("provider_id"),
        "provider_name": data.get("provider_name"),
        "title": data.get("title"),
        "action": data.get("action"),
        "operation": data.get("operation"),
    }
    words = " ".join(_flatten_strings(inspected)).lower().replace("-", "_")
    tokens = {token for part in words.split() for token in part.split("_") if token}
    return bool(tokens & _ACTION_KEYWORDS)


def _agent_has_tools(data: Mapping[str, Any]) -> bool:
    direct = data.get("tools")
    if isinstance(direct, list) and direct:
        return True
    params = data.get("agent_parameters")
    if not isinstance(params, Mapping):
        return False
    tools_config = params.get("tools")
    if isinstance(tools_config, Mapping):
        value = tools_config.get("value")
        return isinstance(value, list) and bool(value)
    return isinstance(tools_config, list) and bool(tools_config)


def _extract_iteration_limit(node: _Node) -> int | None:
    candidates: list[Any] = [
        node.data.get("loop_count"),
        node.data.get("max_iteration"),
        node.data.get("max_iterations"),
    ]
    params = node.data.get("agent_parameters")
    if isinstance(params, Mapping):
        candidates.extend([params.get("max_iteration"), params.get("max_iterations")])
        strategy = params.get("strategy")
        if isinstance(strategy, Mapping):
            candidates.extend([strategy.get("max_iteration"), strategy.get("max_iterations")])
    for value in candidates:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        if isinstance(value, Mapping):
            nested = value.get("value")
            if isinstance(nested, int):
                return nested
            if isinstance(nested, str) and nested.isdigit():
                return int(nested)
    return None


def _extract_temperature(data: Mapping[str, Any]) -> float | None:
    candidates: list[Any] = []
    model_parameters = data.get("model_parameters")
    if isinstance(model_parameters, Mapping):
        candidates.append(model_parameters.get("temperature"))
    model = data.get("model")
    if isinstance(model, Mapping):
        candidates.append(model.get("temperature"))
        completion = model.get("completion_params")
        if isinstance(completion, Mapping):
            candidates.append(completion.get("temperature"))
    agent_params = data.get("agent_parameters")
    if isinstance(agent_params, Mapping):
        model_config = agent_params.get("model")
        if isinstance(model_config, Mapping):
            model_value = model_config.get("value", model_config)
            if isinstance(model_value, Mapping):
                completion = model_value.get("completion_params")
                if isinstance(completion, Mapping):
                    candidates.append(completion.get("temperature"))
                candidates.append(model_value.get("temperature"))
    for value in candidates:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass
    return None


def _reachable(start: str, adjacency: Mapping[str, set[str]]) -> set[str]:
    visited: set[str] = set()
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        queue.extend(adjacency.get(current, ()))
    return visited


def _has_path(source: str, target: str, adjacency: Mapping[str, set[str]]) -> bool:
    if source == target:
        return True
    return target in _reachable(source, adjacency)


def _cycle_components(node_ids: set[str], adjacency: Mapping[str, set[str]]) -> tuple[frozenset[str], ...]:
    """Return the strongly connected components that form directed cycles.

    A Kahn topological remainder also includes acyclic nodes downstream of a cycle,
    which creates false positives in governance reports. Tarjan's algorithm isolates
    exact cyclic components in O(V + E).
    """

    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[frozenset[str]] = []

    def strong_connect(node_id: str) -> None:
        nonlocal index
        indices[node_id] = index
        lowlinks[node_id] = index
        index += 1
        stack.append(node_id)
        on_stack.add(node_id)

        for target in adjacency.get(node_id, ()):
            if target not in node_ids:
                continue
            if target not in indices:
                strong_connect(target)
                lowlinks[node_id] = min(lowlinks[node_id], lowlinks[target])
            elif target in on_stack:
                lowlinks[node_id] = min(lowlinks[node_id], indices[target])

        if lowlinks[node_id] != indices[node_id]:
            return

        component: set[str] = set()
        while stack:
            member = stack.pop()
            on_stack.remove(member)
            component.add(member)
            if member == node_id:
                break

        if len(component) > 1:
            components.append(frozenset(component))
        elif component:
            member = next(iter(component))
            if member in adjacency.get(member, ()):
                components.append(frozenset(component))

    for node_id in sorted(node_ids):
        if node_id not in indices:
            strong_connect(node_id)
    return tuple(sorted(components, key=lambda component: tuple(sorted(component))))


def _risk_level(score: int) -> RiskLevel:
    if score >= 70:
        return RiskLevel.CRITICAL
    if score >= 40:
        return RiskLevel.HIGH
    if score >= 20:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def _policy_decision(
    *,
    mode: GovernanceMode,
    findings: Sequence[WorkflowFinding],
    risk_score: int,
    max_risk_score: int | None,
) -> tuple[bool, tuple[str, ...]]:
    if mode in {GovernanceMode.OFF, GovernanceMode.ADVISORY}:
        return False, ()

    reasons: list[str] = []
    if mode == GovernanceMode.STANDARD:
        critical = [finding.code for finding in findings if finding.severity == FindingSeverity.CRITICAL]
        structural = [finding.code for finding in findings if finding.code in _STANDARD_STRUCTURAL_BLOCKERS]
        if critical:
            reasons.append(f"critical findings: {', '.join(sorted(critical))}")
        if structural:
            reasons.append(f"non-executable graph findings: {', '.join(sorted(structural))}")
        threshold = 75 if max_risk_score is None else max_risk_score
    else:
        severe = [
            finding.code
            for finding in findings
            if finding.severity in {FindingSeverity.HIGH, FindingSeverity.CRITICAL}
        ]
        if severe:
            reasons.append(f"high-assurance findings: {', '.join(sorted(severe))}")
        threshold = 45 if max_risk_score is None else max_risk_score

    if risk_score > threshold:
        reasons.append(f"risk score {risk_score} exceeds policy threshold {threshold}")
    return bool(reasons), tuple(reasons)


def audit_workflow_graph(
    graph: Mapping[str, Any],
    *,
    mode: GovernanceMode | str = GovernanceMode.ADVISORY,
    max_risk_score: int | None = None,
    require_human_approval_for_external_actions: bool = False,
) -> WorkflowAuditReport:
    """Statically analyze a workflow graph before it is published.

    The analyzer is deterministic and does not call a model. It evaluates graph
    integrity, excessive agency, indirect prompt-injection exposure, resource
    bounds, embedded secrets, human oversight, and semantic reproducibility.
    """

    if isinstance(mode, str):
        mode = GovernanceMode(mode)
    if max_risk_score is not None and not 0 <= max_risk_score <= 100:
        raise ValueError("max_risk_score must be between 0 and 100")

    raw_nodes = graph.get("nodes")
    raw_edges = graph.get("edges")
    findings: list[WorkflowFinding] = []

    if not isinstance(raw_nodes, list):
        raw_nodes = []
        findings.append(
            WorkflowFinding(
                code="graph.nodes.invalid",
                severity=FindingSeverity.CRITICAL,
                title="Graph nodes are not a list",
                detail="The workflow graph cannot be analyzed or executed safely because its nodes field is malformed.",
                recommendation="Regenerate or repair the workflow DSL before publication.",
            )
        )
    if not isinstance(raw_edges, list):
        raw_edges = []
        findings.append(
            WorkflowFinding(
                code="graph.edges.invalid",
                severity=FindingSeverity.CRITICAL,
                title="Graph edges are not a list",
                detail="The workflow graph cannot be analyzed or executed safely because its edges field is malformed.",
                recommendation="Regenerate or repair the workflow DSL before publication.",
            )
        )

    parsed_nodes: list[_Node] = []
    id_counts: Counter[str] = Counter()
    for index, raw_node in enumerate(raw_nodes):
        if not isinstance(raw_node, Mapping):
            findings.append(
                WorkflowFinding(
                    code="graph.node.invalid",
                    severity=FindingSeverity.HIGH,
                    title="Invalid node object",
                    detail=f"Node at index {index} is not an object and will be ignored by the governance analyzer.",
                    recommendation="Remove the malformed node or replace it with a valid workflow node object.",
                )
            )
            continue
        raw_id = raw_node.get("id")
        node_id = raw_id if isinstance(raw_id, str) and raw_id else f"<missing:{index}>"
        if node_id.startswith("<missing:"):
            findings.append(
                WorkflowFinding(
                    code="graph.node.missing_id",
                    severity=FindingSeverity.CRITICAL,
                    title="Node is missing an identifier",
                    detail=f"Node at index {index} has no stable id.",
                    recommendation="Assign a unique node id before publication.",
                )
            )
        id_counts[node_id] += 1
        data = _node_data(raw_node)
        parsed_nodes.append(
            _Node(
                node_id=node_id,
                node_type=_node_type(raw_node),
                raw=raw_node,
                data=data,
                nested=_is_nested(raw_node, data),
            )
        )

    duplicate_ids = sorted(node_id for node_id, count in id_counts.items() if count > 1)
    if duplicate_ids:
        findings.append(
            WorkflowFinding(
                code="graph.node.duplicate_id",
                severity=FindingSeverity.CRITICAL,
                title="Duplicate node identifiers",
                detail="Duplicate ids make graph routing ambiguous and can corrupt execution state.",
                recommendation="Assign a unique id to every node.",
                node_ids=tuple(duplicate_ids),
            )
        )

    nodes_by_id = {node.node_id: node for node in parsed_nodes}
    node_ids = set(nodes_by_id)
    parsed_edges: list[_Edge] = []
    dangling_edges: list[tuple[str, str]] = []
    self_loops: list[str] = []
    for raw_edge in raw_edges:
        if not isinstance(raw_edge, Mapping):
            findings.append(
                WorkflowFinding(
                    code="graph.edge.invalid",
                    severity=FindingSeverity.HIGH,
                    title="Invalid edge object",
                    detail="At least one edge is not an object and cannot be routed safely.",
                    recommendation="Remove malformed edges before publication.",
                )
            )
            continue
        source = raw_edge.get("source")
        target = raw_edge.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            findings.append(
                WorkflowFinding(
                    code="graph.edge.missing_endpoint",
                    severity=FindingSeverity.HIGH,
                    title="Edge endpoint is missing",
                    detail="An edge has no valid source or target id.",
                    recommendation="Reconnect or delete the malformed edge.",
                )
            )
            continue
        parsed_edges.append(_Edge(source=source, target=target, raw=raw_edge))
        if source not in node_ids or target not in node_ids:
            dangling_edges.append((source, target))
        if source == target:
            self_loops.append(source)

    if dangling_edges:
        findings.append(
            WorkflowFinding(
                code="graph.edge.dangling",
                severity=FindingSeverity.HIGH,
                title="Edges reference missing nodes",
                detail="Dangling edges make execution paths incomplete and can fail only after deployment.",
                recommendation="Remove dangling edges or restore their missing nodes.",
                node_ids=tuple(sorted({node_id for edge in dangling_edges for node_id in edge})),
                evidence={"edges": [{"source": source, "target": target} for source, target in dangling_edges[:20]]},
            )
        )

    if self_loops:
        findings.append(
            WorkflowFinding(
                code="graph.edge.self_loop",
                severity=FindingSeverity.MEDIUM,
                title="Direct self-loop detected",
                detail="A node routes directly to itself, which can create non-terminating execution outside a bounded loop construct.",
                recommendation="Use the explicit Loop or Iteration node and configure a finite bound.",
                node_ids=tuple(sorted(set(self_loops))),
            )
        )

    adjacency: dict[str, set[str]] = defaultdict(set)
    reverse: dict[str, set[str]] = defaultdict(set)
    for edge in parsed_edges:
        if edge.source in node_ids and edge.target in node_ids:
            adjacency[edge.source].add(edge.target)
            reverse[edge.target].add(edge.source)

    node_type_counts = Counter(node.node_type for node in parsed_nodes)
    if not parsed_nodes:
        findings.append(
            WorkflowFinding(
                code="graph.empty",
                severity=FindingSeverity.HIGH,
                title="Workflow graph is empty",
                detail="An empty workflow has no executable behavior.",
                recommendation="Add an entry node, processing nodes, and an explicit terminal node.",
            )
        )

    top_level_nodes = [node for node in parsed_nodes if not node.nested]
    explicit_entries = [node for node in top_level_nodes if node.node_type in _ENTRY_TYPES]
    implicit_entries = [node for node in top_level_nodes if not reverse.get(node.node_id)]
    entry_nodes = explicit_entries or implicit_entries
    explicit_terminals = [node for node in top_level_nodes if node.node_type in _TERMINAL_TYPES]
    implicit_terminals = [node for node in top_level_nodes if not adjacency.get(node.node_id)]
    terminal_nodes = explicit_terminals or implicit_terminals

    if top_level_nodes and not explicit_entries:
        findings.append(
            WorkflowFinding(
                code="graph.entry.implicit",
                severity=FindingSeverity.MEDIUM,
                title="No explicit workflow entry node",
                detail="The graph relies on a node with no inbound edge rather than a recognized Start or Trigger node.",
                recommendation="Add an explicit Start, Webhook Trigger, Schedule Trigger, Plugin Trigger, or Datasource entry.",
                node_ids=tuple(sorted(node.node_id for node in entry_nodes)),
            )
        )
    if top_level_nodes and not explicit_terminals:
        findings.append(
            WorkflowFinding(
                code="graph.terminal.implicit",
                severity=FindingSeverity.MEDIUM,
                title="No explicit terminal node",
                detail="The graph has no recognized End, Answer, or Knowledge Index node.",
                recommendation="Add an explicit terminal node so outputs and completion semantics are unambiguous.",
                node_ids=tuple(sorted(node.node_id for node in terminal_nodes)),
            )
        )

    reachable_from_entries: set[str] = set()
    for entry in entry_nodes:
        reachable_from_entries.update(_reachable(entry.node_id, adjacency))
    unreachable = sorted(node.node_id for node in top_level_nodes if node.node_id not in reachable_from_entries)
    if unreachable:
        findings.append(
            WorkflowFinding(
                code="graph.node.unreachable",
                severity=FindingSeverity.MEDIUM,
                title="Unreachable workflow nodes",
                detail="These top-level nodes cannot be reached from any workflow entry and will never execute.",
                recommendation="Connect the nodes to a valid path or delete them.",
                node_ids=tuple(unreachable),
            )
        )

    orphans = sorted(
        node.node_id
        for node in top_level_nodes
        if node.node_id not in {entry.node_id for entry in entry_nodes}
        and node.node_id not in {terminal.node_id for terminal in terminal_nodes}
        and not adjacency.get(node.node_id)
        and not reverse.get(node.node_id)
    )
    if orphans:
        findings.append(
            WorkflowFinding(
                code="graph.node.orphan",
                severity=FindingSeverity.MEDIUM,
                title="Disconnected orphan nodes",
                detail="Orphan nodes increase maintenance risk and can hide stale prompts, credentials, or tools.",
                recommendation="Delete unused nodes or connect them to an intentional execution path.",
                node_ids=tuple(orphans),
            )
        )

    for entry in entry_nodes:
        entry_reachable = _reachable(entry.node_id, adjacency)
        if terminal_nodes and not any(terminal.node_id in entry_reachable for terminal in terminal_nodes):
            findings.append(
                WorkflowFinding(
                    code="graph.path.no_terminal",
                    severity=FindingSeverity.HIGH,
                    title="Entry path cannot reach a terminal",
                    detail="At least one entry can start a run that has no path to a terminal node.",
                    recommendation="Connect every entry path to an explicit End, Answer, or Knowledge Index node.",
                    node_ids=(entry.node_id,),
                )
            )

    cycle_components = _cycle_components(node_ids, adjacency)
    bounded_components = [
        component
        for component in cycle_components
        if any(nodes_by_id[node_id].node_type in _LOOP_TYPES for node_id in component)
    ]
    unbounded_components = [component for component in cycle_components if component not in bounded_components]
    if unbounded_components:
        unbounded_nodes = sorted({node_id for component in unbounded_components for node_id in component})
        findings.append(
            WorkflowFinding(
                code="graph.cycle.unbounded",
                severity=FindingSeverity.HIGH,
                title="Cycle exists outside an explicit bounded loop",
                detail="The graph contains a directed cycle with no recognized Loop or Iteration control node.",
                recommendation="Refactor the cycle into an explicit bounded loop and define a finite iteration count.",
                node_ids=tuple(unbounded_nodes),
                evidence={"components": [sorted(component) for component in unbounded_components]},
            )
        )
    if bounded_components:
        bounded_nodes = sorted({node_id for component in bounded_components for node_id in component})
        findings.append(
            WorkflowFinding(
                code="graph.cycle.bounded_construct",
                severity=FindingSeverity.INFO,
                title="Explicit loop construct detected",
                detail="A directed cycle passes through a recognized Loop or Iteration control node.",
                recommendation="Keep loop bounds conservative and verify termination conditions with tests.",
                node_ids=tuple(bounded_nodes),
                evidence={"components": [sorted(component) for component in bounded_components]},
            )
        )

    sensitive_locations: list[tuple[str, str]] = []
    for node in parsed_nodes:
        for path, _ in _iter_sensitive_values(node.data):
            sensitive_locations.append((node.node_id, ".".join(path)))
    if sensitive_locations:
        findings.append(
            WorkflowFinding(
                code="security.secret.embedded",
                severity=FindingSeverity.CRITICAL,
                title="Possible plaintext secret embedded in workflow graph",
                detail="Credential-like values appear directly in node configuration. Published workflow snapshots and exports can retain them.",
                recommendation="Move secrets to workspace credentials, environment variables, or an external secret manager.",
                node_ids=tuple(sorted({node_id for node_id, _ in sensitive_locations})),
                evidence={
                    "locations": [
                        {"node_id": node_id, "path": path} for node_id, path in sensitive_locations[:20]
                    ]
                },
            )
        )

    actionable_nodes: set[str] = set()
    uncertain_external_nodes: set[str] = set()
    retrieval_nodes: set[str] = set()
    human_nodes: set[str] = set()
    code_nodes: set[str] = set()
    agent_nodes: set[str] = set()
    webhook_entries: set[str] = set()

    for node in parsed_nodes:
        if node.node_type in _HUMAN_TYPES:
            human_nodes.add(node.node_id)
        if node.node_type in _RETRIEVAL_TYPES:
            retrieval_nodes.add(node.node_id)
        if node.node_type in _CODE_TYPES:
            code_nodes.add(node.node_id)
        if node.node_type in _AGENT_TYPES:
            agent_nodes.add(node.node_id)
            if _agent_has_tools(node.data):
                actionable_nodes.add(node.node_id)
        if node.node_type in {"trigger-webhook", "webhook-trigger"}:
            webhook_entries.add(node.node_id)
        if node.node_type in _HTTP_TYPES:
            method = _extract_http_method(node.data)
            if method in _MUTATING_HTTP_METHODS:
                actionable_nodes.add(node.node_id)
            elif method is None:
                uncertain_external_nodes.add(node.node_id)
        if node.node_type in _TOOL_TYPES:
            if _tool_looks_mutating(node.data):
                actionable_nodes.add(node.node_id)
            else:
                uncertain_external_nodes.add(node.node_id)

        limit = _extract_iteration_limit(node)
        if limit is not None and limit > 50:
            findings.append(
                WorkflowFinding(
                    code="resource.iteration.excessive",
                    severity=FindingSeverity.HIGH,
                    title="Excessive iteration limit",
                    detail=f"Node permits up to {limit} iterations, increasing latency, cost, and denial-of-wallet risk.",
                    recommendation="Reduce the bound, add an explicit stop condition, and enforce per-run token and time budgets.",
                    node_ids=(node.node_id,),
                    evidence={"iteration_limit": limit},
                )
            )
        elif limit is not None and limit > 20:
            findings.append(
                WorkflowFinding(
                    code="resource.iteration.high",
                    severity=FindingSeverity.MEDIUM,
                    title="High iteration limit",
                    detail=f"Node permits up to {limit} iterations.",
                    recommendation="Confirm the bound is necessary and add cost, timeout, and termination tests.",
                    node_ids=(node.node_id,),
                    evidence={"iteration_limit": limit},
                )
            )

    if code_nodes:
        findings.append(
            WorkflowFinding(
                code="security.code_execution.present",
                severity=FindingSeverity.LOW,
                title="Code execution nodes are present",
                detail="Code nodes expand the attack surface even when executed in a sandbox.",
                recommendation="Use least-privilege sandbox policies, dependency allowlists, strict timeouts, and output-size limits.",
                node_ids=tuple(sorted(code_nodes)),
            )
        )
    if uncertain_external_nodes:
        findings.append(
            WorkflowFinding(
                code="agency.external_action.unknown_semantics",
                severity=FindingSeverity.LOW,
                title="External tools have unknown side-effect semantics",
                detail="Static analysis could not determine whether these tools are read-only or mutating.",
                recommendation="Document tool permissions and mark high-impact operations for human approval.",
                node_ids=tuple(sorted(uncertain_external_nodes)),
            )
        )

    def has_prior_human_approval(node_id: str) -> bool:
        return any(human_id in _reachable(node_id, reverse) for human_id in human_nodes)

    missing_oversight = sorted(node_id for node_id in actionable_nodes if not has_prior_human_approval(node_id))
    oversight_required = require_human_approval_for_external_actions or mode == GovernanceMode.HIGH_ASSURANCE
    if missing_oversight:
        findings.append(
            WorkflowFinding(
                code="agency.human_oversight.missing",
                severity=FindingSeverity.HIGH if oversight_required else FindingSeverity.MEDIUM,
                title="High-impact actions lack prior human approval",
                detail="Action-capable tools or agents can execute without an explicit Human Input approval gate.",
                recommendation="Place a Human Input approval node immediately before high-impact actions and bind approval to the exact action payload.",
                node_ids=tuple(missing_oversight),
            )
        )

    injection_paths: list[tuple[str, str]] = []
    for retrieval_id in retrieval_nodes:
        for action_id in actionable_nodes:
            if _has_path(retrieval_id, action_id, adjacency) and not has_prior_human_approval(action_id):
                injection_paths.append((retrieval_id, action_id))
    if injection_paths:
        findings.append(
            WorkflowFinding(
                code="security.indirect_prompt_injection.action_path",
                severity=FindingSeverity.HIGH,
                title="Retrieved content can influence an unapproved external action",
                detail="A knowledge-retrieval node has a path to an action-capable tool or agent without a human approval boundary. Malicious retrieved content could steer downstream actions.",
                recommendation="Treat retrieved content as untrusted, isolate instructions from data, validate tool arguments, and require approval before side effects.",
                node_ids=tuple(sorted({node_id for pair in injection_paths for node_id in pair})),
                evidence={
                    "paths": [
                        {"retrieval_node": retrieval, "action_node": action}
                        for retrieval, action in injection_paths[:20]
                    ]
                },
            )
        )

    if webhook_entries and actionable_nodes:
        exposed_actions = sorted(
            action_id
            for action_id in actionable_nodes
            if any(_has_path(entry_id, action_id, adjacency) for entry_id in webhook_entries)
        )
        if exposed_actions:
            findings.append(
                WorkflowFinding(
                    code="security.webhook.side_effect_path",
                    severity=FindingSeverity.MEDIUM,
                    title="Webhook-triggered path can perform external actions",
                    detail="Internet-originated webhook data can reach a mutating HTTP request, tool, or agent action.",
                    recommendation="Require authenticated webhooks, replay protection, schema validation, rate limits, and idempotency keys.",
                    node_ids=tuple(sorted(webhook_entries | set(exposed_actions))),
                )
            )

    high_temperature_nodes: list[str] = []
    for node in parsed_nodes:
        if node.node_type not in {"llm", *_AGENT_TYPES}:
            continue
        temperature = _extract_temperature(node.data)
        if temperature is None or temperature <= 0.7:
            continue
        if any(_has_path(node.node_id, action_id, adjacency) for action_id in actionable_nodes):
            high_temperature_nodes.append(node.node_id)
    if high_temperature_nodes:
        findings.append(
            WorkflowFinding(
                code="reliability.nondeterministic_action_path",
                severity=FindingSeverity.MEDIUM,
                title="High-temperature model output can influence actions",
                detail="Sampling temperature above 0.7 is used on a path that can reach an external action, increasing behavioral variance.",
                recommendation="Use structured outputs, deterministic validation, lower temperature, and action-specific evals before deployment.",
                node_ids=tuple(sorted(high_temperature_nodes)),
            )
        )

    base_risk = 0
    base_risk += min(16, len(code_nodes) * 8)
    base_risk += min(18, len(actionable_nodes) * 6)
    base_risk += min(20, len(agent_nodes) * 10)
    base_risk += min(8, len(webhook_entries) * 4)
    base_risk += min(8, len(retrieval_nodes) * 2)
    base_risk += min(8, sum(node.node_type in _LOOP_TYPES for node in parsed_nodes) * 4)
    finding_risk = sum(_SEVERITY_WEIGHT[finding.severity] for finding in findings)
    risk_score = min(100, base_risk + finding_risk)

    blocked, blocking_reasons = _policy_decision(
        mode=mode,
        findings=findings,
        risk_score=risk_score,
        max_risk_score=max_risk_score,
    )
    findings.sort(key=lambda finding: (-_SEVERITY_WEIGHT[finding.severity], finding.code, finding.node_ids))

    analyzer_version = "2.0.0"
    policy_revision = "orqivium-governance-v2"
    semantic_fingerprint = semantic_workflow_fingerprint(graph)
    policy_payload = {
        "policy_revision": policy_revision,
        "mode": mode.value,
        "max_risk_score": max_risk_score,
        "require_human_approval_for_external_actions": require_human_approval_for_external_actions,
    }
    policy_digest = hashlib.sha256(
        json.dumps(policy_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    policy_fingerprint = f"sha256:{policy_digest}"
    audit_digest = hashlib.sha256(
        f"{semantic_fingerprint}|{policy_fingerprint}|{analyzer_version}".encode("utf-8")
    ).hexdigest()

    return WorkflowAuditReport(
        product="Orqivium",
        schema_version="2.0",
        analyzer_version=analyzer_version,
        fingerprint_algorithm="orqivium-semantic-v1+sha256",
        policy_revision=policy_revision,
        policy_fingerprint=policy_fingerprint,
        audit_id=f"orq_{audit_digest[:24]}",
        governance_mode=mode,
        semantic_fingerprint=semantic_fingerprint,
        risk_score=risk_score,
        risk_level=_risk_level(risk_score),
        node_count=len(parsed_nodes),
        edge_count=len(parsed_edges),
        node_type_counts=dict(node_type_counts),
        findings=tuple(findings),
        blocked=blocked,
        blocking_reasons=blocking_reasons,
    )
