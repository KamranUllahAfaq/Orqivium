from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class GovernanceConfig(BaseSettings):
    """Orqivium workflow publication governance settings."""

    ORQIVIUM_GOVERNANCE_MODE: Literal["off", "advisory", "standard", "high_assurance"] = Field(
        default="advisory",
        description=(
            "Workflow publication policy. advisory logs findings without blocking; standard blocks critical "
            "findings; high_assurance blocks high/critical findings and expects human approval before external actions."
        ),
    )
    ORQIVIUM_GOVERNANCE_MAX_RISK_SCORE: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Optional publication risk threshold overriding the selected governance profile.",
    )
    ORQIVIUM_GOVERNANCE_REQUIRE_HUMAN_APPROVAL_FOR_EXTERNAL_ACTIONS: bool = Field(
        default=False,
        description="Elevate missing human approval before action-capable nodes to a high-severity finding.",
    )
    ORQIVIUM_GOVERNANCE_AUDIT_LOG_ENABLED: bool = Field(
        default=True,
        description="Emit a compact machine-readable governance audit event whenever a workflow is published.",
    )
