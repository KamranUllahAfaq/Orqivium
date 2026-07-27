from core.governance import (
    GovernanceMode,
    WorkflowGovernanceViolationError,
    audit_for_publication,
    audit_workflow_graph,
    semantic_workflow_fingerprint,
)


def _graph(nodes, edges):
    return {"nodes": nodes, "edges": edges, "viewport": {"x": 10, "y": 20, "zoom": 0.7}}


def test_semantic_fingerprint_ignores_editor_layout():
    graph_a = _graph(
        [
            {"id": "start", "position": {"x": 0, "y": 0}, "data": {"type": "start"}},
            {"id": "end", "position": {"x": 100, "y": 100}, "data": {"type": "end"}},
        ],
        [{"id": "edge-a", "source": "start", "target": "end"}],
    )
    graph_b = _graph(
        [
            {"id": "end", "position": {"x": 900, "y": 400}, "data": {"type": "end"}},
            {"id": "start", "position": {"x": 300, "y": 100}, "data": {"type": "start"}},
        ],
        [{"id": "edge-b", "source": "start", "target": "end", "selected": True}],
    )
    graph_b["viewport"] = {"x": -100, "y": 99, "zoom": 1.2}

    assert semantic_workflow_fingerprint(graph_a) == semantic_workflow_fingerprint(graph_b)


def test_fingerprint_changes_when_prompt_semantics_change():
    base = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "llm", "data": {"type": "llm", "prompt_template": [{"role": "user", "text": "A"}]}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [{"source": "start", "target": "llm"}, {"source": "llm", "target": "end"}],
    )
    changed = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "llm", "data": {"type": "llm", "prompt_template": [{"role": "user", "text": "B"}]}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [{"source": "start", "target": "llm"}, {"source": "llm", "target": "end"}],
    )

    assert semantic_workflow_fingerprint(base) != semantic_workflow_fingerprint(changed)


def test_clean_read_only_workflow_passes_standard_policy():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "llm", "data": {"type": "llm", "model_parameters": {"temperature": 0.2}}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [{"source": "start", "target": "llm"}, {"source": "llm", "target": "end"}],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.STANDARD)

    assert report.blocked is False
    assert report.semantic_fingerprint.startswith("sha256:")
    assert report.node_count == 3


def test_dangling_edge_blocks_standard_policy():
    graph = _graph(
        [{"id": "start", "data": {"type": "start"}}],
        [{"source": "start", "target": "missing"}],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.STANDARD, max_risk_score=100)

    assert report.blocked is True
    assert "graph.edge.dangling" in {finding.code for finding in report.findings}


def test_plaintext_secret_is_critical_and_blocks_standard():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {
                "id": "http",
                "data": {
                    "type": "http-request",
                    "method": "GET",
                    "headers": {"api_key": "sk-live-1234567890"},
                },
            },
            {"id": "end", "data": {"type": "end"}},
        ],
        [{"source": "start", "target": "http"}, {"source": "http", "target": "end"}],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.STANDARD, max_risk_score=100)

    assert report.blocked is True
    assert "security.secret.embedded" in {finding.code for finding in report.findings}


def test_retrieval_to_mutating_http_without_human_is_high_risk():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "rag", "data": {"type": "knowledge-retrieval"}},
            {"id": "post", "data": {"type": "http-request", "method": "POST"}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [
            {"source": "start", "target": "rag"},
            {"source": "rag", "target": "post"},
            {"source": "post", "target": "end"},
        ],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.HIGH_ASSURANCE)
    codes = {finding.code for finding in report.findings}

    assert "security.indirect_prompt_injection.action_path" in codes
    assert "agency.human_oversight.missing" in codes
    assert report.blocked is True


def test_human_approval_reduces_action_oversight_finding():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "approval", "data": {"type": "human-input"}},
            {"id": "post", "data": {"type": "http-request", "method": "POST"}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [
            {"source": "start", "target": "approval"},
            {"source": "approval", "target": "post"},
            {"source": "post", "target": "end"},
        ],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.HIGH_ASSURANCE, max_risk_score=100)

    assert "agency.human_oversight.missing" not in {finding.code for finding in report.findings}


def test_cycle_detection_excludes_downstream_acyclic_nodes():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "a", "data": {"type": "llm"}},
            {"id": "b", "data": {"type": "llm"}},
            {"id": "after", "data": {"type": "llm"}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [
            {"source": "start", "target": "a"},
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
            {"source": "b", "target": "after"},
            {"source": "after", "target": "end"},
        ],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.ADVISORY)
    cycle_finding = next(finding for finding in report.findings if finding.code == "graph.cycle.unbounded")

    assert set(cycle_finding.node_ids) == {"a", "b"}


def test_explicit_entry_makes_disconnected_island_unreachable():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "end", "data": {"type": "end"}},
            {"id": "island", "data": {"type": "llm"}},
        ],
        [{"source": "start", "target": "end"}],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.ADVISORY)
    finding = next(finding for finding in report.findings if finding.code == "graph.node.unreachable")

    assert finding.node_ids == ("island",)


def test_cycle_with_explicit_loop_is_classified_as_bounded_construct():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "loop", "data": {"type": "loop", "loop_count": 5}},
            {"id": "work", "data": {"type": "llm"}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [
            {"source": "start", "target": "loop"},
            {"source": "loop", "target": "work"},
            {"source": "work", "target": "loop"},
            {"source": "loop", "target": "end"},
        ],
    )

    report = audit_workflow_graph(graph, mode=GovernanceMode.ADVISORY)
    codes = {finding.code for finding in report.findings}

    assert "graph.cycle.bounded_construct" in codes
    assert "graph.cycle.unbounded" not in codes


def test_publication_exception_is_actionable_without_exposing_secret_value():
    graph = _graph(
        [
            {"id": "start", "data": {"type": "start"}},
            {"id": "http", "data": {"type": "http-request", "api_key": "sk-live-1234567890"}},
            {"id": "end", "data": {"type": "end"}},
        ],
        [{"source": "start", "target": "http"}, {"source": "http", "target": "end"}],
    )

    try:
        audit_for_publication(graph, mode=GovernanceMode.STANDARD, max_risk_score=100, emit_audit_log=False)
    except WorkflowGovernanceViolationError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected publication to be blocked")

    assert "security.secret.embedded" in message
    assert "sk-live-1234567890" not in message
