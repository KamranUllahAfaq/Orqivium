from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

_NODE_EDITOR_KEYS = {
    "position",
    "positionAbsolute",
    "selected",
    "dragging",
    "width",
    "height",
    "measured",
    "zIndex",
}
_EDGE_EDITOR_KEYS = {
    "id",
    "selected",
    "animated",
    "zIndex",
}
_GRAPH_EDITOR_KEYS = {"viewport"}


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _normalize(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize(item) for item in value]
    return value


def _canonical_node(node: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize({key: value for key, value in node.items() if key not in _NODE_EDITOR_KEYS})


def _canonical_edge(edge: Mapping[str, Any]) -> dict[str, Any]:
    return _normalize({key: value for key, value in edge.items() if key not in _EDGE_EDITOR_KEYS})


def canonicalize_workflow_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic representation of runtime-relevant workflow semantics.

    ReactFlow coordinates, selection state, viewport state, measured dimensions, and
    transient edge identifiers are deliberately excluded. Prompt order, variable
    order, tool parameters, node configuration, and edge routing are preserved.
    """

    canonical: dict[str, Any] = {
        key: value for key, value in graph.items() if key not in _GRAPH_EDITOR_KEYS and key not in {"nodes", "edges"}
    }

    raw_nodes = graph.get("nodes")
    nodes = [node for node in raw_nodes if isinstance(node, Mapping)] if isinstance(raw_nodes, list) else []
    canonical["nodes"] = sorted(
        (_canonical_node(node) for node in nodes),
        key=lambda item: (str(item.get("id", "")), json.dumps(item, sort_keys=True, default=str)),
    )

    raw_edges = graph.get("edges")
    edges = [edge for edge in raw_edges if isinstance(edge, Mapping)] if isinstance(raw_edges, list) else []
    canonical["edges"] = sorted(
        (_canonical_edge(edge) for edge in edges),
        key=lambda item: (
            str(item.get("source", "")),
            str(item.get("sourceHandle", "")),
            str(item.get("target", "")),
            str(item.get("targetHandle", "")),
            json.dumps(item, sort_keys=True, default=str),
        ),
    )
    return _normalize(canonical)


def semantic_workflow_fingerprint(graph: Mapping[str, Any]) -> str:
    canonical = canonicalize_workflow_graph(graph)
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"
