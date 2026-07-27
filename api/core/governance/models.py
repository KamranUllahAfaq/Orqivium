from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class GovernanceMode(StrEnum):
    """Publication policy profile for the Orqivium control plane."""

    OFF = "off"
    ADVISORY = "advisory"
    STANDARD = "standard"
    HIGH_ASSURANCE = "high_assurance"


class FindingSeverity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class WorkflowFinding:
    code: str
    severity: FindingSeverity
    title: str
    detail: str
    recommendation: str
    node_ids: tuple[str, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["severity"] = self.severity.value
        payload["node_ids"] = list(self.node_ids)
        return payload


@dataclass(frozen=True, slots=True)
class WorkflowAuditReport:
    product: str
    schema_version: str
    analyzer_version: str
    fingerprint_algorithm: str
    policy_revision: str
    policy_fingerprint: str
    audit_id: str
    governance_mode: GovernanceMode
    semantic_fingerprint: str
    risk_score: int
    risk_level: RiskLevel
    node_count: int
    edge_count: int
    node_type_counts: dict[str, int]
    findings: tuple[WorkflowFinding, ...]
    blocked: bool
    blocking_reasons: tuple[str, ...]

    @property
    def critical_count(self) -> int:
        return sum(f.severity == FindingSeverity.CRITICAL for f in self.findings)

    @property
    def high_count(self) -> int:
        return sum(f.severity == FindingSeverity.HIGH for f in self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "product": self.product,
            "schema_version": self.schema_version,
            "analyzer_version": self.analyzer_version,
            "fingerprint_algorithm": self.fingerprint_algorithm,
            "policy_revision": self.policy_revision,
            "policy_fingerprint": self.policy_fingerprint,
            "audit_id": self.audit_id,
            "governance_mode": self.governance_mode.value,
            "semantic_fingerprint": self.semantic_fingerprint,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "node_type_counts": dict(sorted(self.node_type_counts.items())),
            "findings": [finding.to_dict() for finding in self.findings],
            "blocked": self.blocked,
            "blocking_reasons": list(self.blocking_reasons),
        }

    def to_markdown(self) -> str:
        status = "BLOCKED" if self.blocked else "PASS"
        lines = [
            "# Orqivium Workflow Audit",
            "",
            f"- **Audit ID:** `{self.audit_id}`",
            f"- **Decision:** {status}",
            f"- **Policy:** `{self.governance_mode.value}`",
            f"- **Analyzer:** `{self.analyzer_version}`",
            f"- **Policy revision:** `{self.policy_revision}`",
            f"- **Policy fingerprint:** `{self.policy_fingerprint}`",
            f"- **Risk:** {self.risk_score}/100 ({self.risk_level.value})",
            f"- **Semantic fingerprint:** `{self.semantic_fingerprint}`",
            f"- **Graph size:** {self.node_count} nodes / {self.edge_count} edges",
            "",
            "## Findings",
            "",
        ]
        if not self.findings:
            lines.append("No findings.")
            return "\n".join(lines) + "\n"

        for finding in self.findings:
            nodes = f" Nodes: `{', '.join(finding.node_ids)}`." if finding.node_ids else ""
            lines.extend(
                [
                    f"### [{finding.severity.value.upper()}] {finding.title}",
                    "",
                    f"{finding.detail}{nodes}",
                    "",
                    f"**Recommendation:** {finding.recommendation}",
                    "",
                ]
            )
        if self.blocking_reasons:
            lines.extend(["## Blocking reasons", ""])
            lines.extend(f"- {reason}" for reason in self.blocking_reasons)
            lines.append("")
        return "\n".join(lines)
