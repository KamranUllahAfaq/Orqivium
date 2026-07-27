from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

from .analyzer import audit_workflow_graph
from .models import GovernanceMode, WorkflowAuditReport

logger = logging.getLogger(__name__)


class WorkflowGovernanceViolationError(ValueError):
    def __init__(self, report: WorkflowAuditReport):
        self.report = report
        reason = "; ".join(report.blocking_reasons) or "workflow governance policy rejected publication"
        severe = [
            finding
            for finding in report.findings
            if finding.severity.value in {"high", "critical"}
        ][:3]
        finding_summary = "; ".join(
            f"[{finding.severity.value}] {finding.code}: {finding.title}" for finding in severe
        )
        detail = f"{reason}; {finding_summary}" if finding_summary else reason
        super().__init__(f"Orqivium governance blocked workflow publication: {detail}")


def audit_for_publication(
    graph: Mapping[str, Any],
    *,
    mode: GovernanceMode | str,
    max_risk_score: int | None = None,
    require_human_approval_for_external_actions: bool = False,
    emit_audit_log: bool = True,
) -> WorkflowAuditReport:
    report = audit_workflow_graph(
        graph,
        mode=mode,
        max_risk_score=max_risk_score,
        require_human_approval_for_external_actions=require_human_approval_for_external_actions,
    )
    if emit_audit_log and report.governance_mode != GovernanceMode.OFF:
        logger.info(
            "Orqivium workflow governance audit: %s",
            json.dumps(
                {
                    "audit_id": report.audit_id,
                    "fingerprint": report.semantic_fingerprint,
                    "fingerprint_algorithm": report.fingerprint_algorithm,
                    "analyzer_version": report.analyzer_version,
                    "policy_revision": report.policy_revision,
                    "policy_fingerprint": report.policy_fingerprint,
                    "mode": report.governance_mode.value,
                    "risk_score": report.risk_score,
                    "risk_level": report.risk_level.value,
                    "blocked": report.blocked,
                    "finding_codes": [finding.code for finding in report.findings],
                },
                sort_keys=True,
            ),
        )
    if report.blocked:
        raise WorkflowGovernanceViolationError(report)
    return report
