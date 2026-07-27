from __future__ import annotations

import importlib
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_orqivium_agent_examples_are_importable_from_repo_checkout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(PROJECT_ROOT / "examples" / "orqivium_agent"))

    for module_name in [
        "orqivium_agent_examples.run_pydantic_ai_agent",
        "orqivium_agent_examples.run_server_consumer",
        "orqivium_agent_examples.run_server_sse_consumer",
        "orqivium_agent_examples.run_server_sync_client",
    ]:
        importlib.import_module(module_name)
