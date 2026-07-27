"""Contract tests for the orqivium.drive declaration layer (ENG-623)."""

import pytest
from pydantic import ValidationError

from orqivium_agent.layers.drive import (
    ORQIVIUM_DRIVE_LAYER_TYPE_ID,
    OrqiviumDriveLayerConfig,
    OrqiviumDriveSkillConfig,
)
from orqivium_agent.layers.drive.layer import OrqiviumDriveLayer


def test_type_id_is_frozen_contract() -> None:
    assert ORQIVIUM_DRIVE_LAYER_TYPE_ID == "orqivium.drive"
    assert OrqiviumDriveLayer.type_id == ORQIVIUM_DRIVE_LAYER_TYPE_ID


def test_layer_config_round_trips_manifest_entries() -> None:
    config = OrqiviumDriveLayerConfig.model_validate(
        {
            "drive_ref": "agent-019e9112",
            "skills": [
                {
                    "path": "tender-analyzer",
                    "name": "Tender Analyzer",
                    "description": "Parses RFP documents step by step.",
                    "skill_md_key": "tender-analyzer/SKILL.md",
                    "archive_key": "tender-analyzer/.ORQIVIUM-SKILL-FULL.zip",
                }
            ],
            "mentioned_skill_keys": ["tender-analyzer/SKILL.md"],
            "mentioned_file_keys": ["files/sample.pdf"],
        }
    )

    dumped = config.model_dump(mode="json")
    assert dumped["drive_ref"] == "agent-019e9112"
    assert "drive_base" not in dumped
    assert dumped["skills"][0]["skill_md_key"] == "tender-analyzer/SKILL.md"
    assert dumped["mentioned_file_keys"] == ["files/sample.pdf"]
    assert "content" not in OrqiviumDriveSkillConfig.model_fields


def test_layer_config_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        OrqiviumDriveLayerConfig.model_validate({"drive_ref": "agent-1", "skill_md_body": "# inline content"})


def test_drive_layer_is_registered_and_constructible_from_config() -> None:
    layer = OrqiviumDriveLayer.from_config(
        OrqiviumDriveLayerConfig(drive_ref="agent-1", skills=[], mentioned_skill_keys=[], mentioned_file_keys=[]),
    )

    assert isinstance(layer, OrqiviumDriveLayer)
    assert layer.config.drive_ref == "agent-1"
    assert not hasattr(layer, "local_drive_base")
