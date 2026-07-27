#!/usr/bin/env python3
"""Audit an Orqivium workflow DSL or graph without starting the platform."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPOSITORY_ROOT / "api"
sys.path.insert(0, str(API_ROOT))

from core.governance import GovernanceMode, audit_workflow_graph  # noqa: E402


def _load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    else:
        try:
            import yaml
        except ImportError as exc:
            raise SystemExit("YAML input requires PyYAML. Use `uv run python scripts/orqivium_workflow_audit.py ...`.") from exc
        payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise SystemExit("Input must decode to an object.")

    candidates = [
        payload,
        payload.get("graph"),
        payload.get("workflow", {}).get("graph") if isinstance(payload.get("workflow"), dict) else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, dict) and isinstance(candidate.get("nodes"), list):
            return candidate
    raise SystemExit("Could not locate a workflow graph with `nodes` and `edges` fields.")


def _bounded_risk_score(value: str) -> int:
    parsed = int(value)
    if not 0 <= parsed <= 100:
        raise argparse.ArgumentTypeError("risk score must be between 0 and 100")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Workflow graph JSON or exported YAML/JSON DSL")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in GovernanceMode],
        default=GovernanceMode.STANDARD.value,
        help="Governance policy profile",
    )
    parser.add_argument("--max-risk-score", type=_bounded_risk_score, default=None)
    parser.add_argument("--require-human-approval", action="store_true")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    graph = _load_payload(args.input)
    report = audit_workflow_graph(
        graph,
        mode=args.mode,
        max_risk_score=args.max_risk_score,
        require_human_approval_for_external_actions=args.require_human_approval,
    )
    rendered = json.dumps(report.to_dict(), indent=2, ensure_ascii=False) if args.format == "json" else report.to_markdown()
    if args.output:
        args.output.write_text(rendered + ("\n" if args.format == "json" else ""), encoding="utf-8")
    else:
        print(rendered)
    return 2 if report.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
