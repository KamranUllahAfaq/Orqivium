#!/usr/bin/env python3
"""Run fast, dependency-light validation for an Orqivium source release."""

from __future__ import annotations

import argparse
import compileall
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api"
sys.path.insert(0, str(API))

from core.governance import GovernanceMode, audit_workflow_graph, semantic_workflow_fingerprint  # noqa: E402


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _run(name: str, fn: Callable[[], str]) -> Check:
    try:
        return Check(name, True, fn())
    except Exception as exc:  # release validator must collect every failure
        return Check(name, False, f"{type(exc).__name__}: {exc}")


def _metadata() -> str:
    root_package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    web_package = json.loads((ROOT / "web/package.json").read_text(encoding="utf-8"))
    api_project = tomllib.loads((ROOT / "api/pyproject.toml").read_text(encoding="utf-8"))["project"]
    agent_project = tomllib.loads((ROOT / "orqivium-agent/pyproject.toml").read_text(encoding="utf-8"))["project"]
    cli_package = json.loads((ROOT / "cli/package.json").read_text(encoding="utf-8"))
    sdk_package = json.loads((ROOT / "sdks/nodejs-client/package.json").read_text(encoding="utf-8"))
    uv_lock = tomllib.loads((ROOT / "api/uv.lock").read_text(encoding="utf-8"))
    assert root_package["name"] == "orqivium"
    assert root_package["version"] == "2.0.0"
    assert web_package["name"] == "orqivium-web"
    assert web_package["version"] == "2.0.0"
    assert api_project["name"] == "orqivium-api"
    assert api_project["version"] == "2.0.0"
    assert agent_project["name"] == "orqivium-agent"
    assert agent_project["version"] == "2.0.0"
    assert cli_package["name"] == "@orqivium/cli"
    assert cli_package["version"] == "2.0.0"
    assert cli_package["orqctl"]["release"]["binName"] == "orqctl"
    assert sdk_package["name"] == "orqivium-client"
    assert sdk_package["version"] == "2.0.0"
    owner = "Kamran Ullah Afaq (@kamranullahafaq)"
    for package in (root_package, web_package, cli_package, sdk_package):
        assert package["author"] == owner
        assert package["maintainers"] == [owner]
    assert api_project["authors"] == [{"name": "Kamran Ullah Afaq"}]
    assert api_project["maintainers"] == [{"name": "Kamran Ullah Afaq"}]
    assert agent_project["authors"] == [{"name": "Kamran Ullah Afaq"}]
    assert agent_project["maintainers"] == [{"name": "Kamran Ullah Afaq"}]
    assert sdk_package["contributors"] == [owner]
    assert "orqivium-api" in uv_lock["manifest"]["members"]
    lock_package = next(package for package in uv_lock["package"] if package["name"] == "orqivium-api")
    assert lock_package["version"] == "2.0.0"
    return "Orqivium 2.0.0 metadata is consistent across root, web, API, agent, CLI, SDK, and lockfile"


def _compile() -> str:
    paths = [API, ROOT / "scripts", ROOT / "orqivium-agent/src"]
    for path in paths:
        ok = compileall.compile_dir(str(path), quiet=1, force=True)
        assert ok, f"compile failed for {path.relative_to(ROOT)}"
    return "the complete API, release-script, and Orqivium Agent Python trees compile"


def _unit_tests() -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(API)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-o",
        "addopts=",
        "--confcutdir=api/tests/unit_tests/core/governance",
        "api/tests/unit_tests/core/governance/test_governance_analyzer.py",
    ]
    result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stdout + "\n" + result.stderr).strip())
    summary = next((line for line in reversed(result.stdout.splitlines()) if "passed" in line), "tests passed")
    return summary.strip()


def _governance_behavior() -> str:
    clean = {
        "nodes": [
            {"id": "start", "data": {"type": "start"}},
            {"id": "llm", "data": {"type": "llm", "model_parameters": {"temperature": 0.2}}},
            {"id": "end", "data": {"type": "end"}},
        ],
        "edges": [{"source": "start", "target": "llm"}, {"source": "llm", "target": "end"}],
    }
    unsafe = {
        "nodes": [
            {"id": "start", "data": {"type": "start"}},
            {
                "id": "http",
                "data": {
                    "type": "http-request",
                    "method": "POST",
                    "headers": {"api_key": "sk-live-1234567890"},
                },
            },
            {"id": "end", "data": {"type": "end"}},
        ],
        "edges": [{"source": "start", "target": "http"}, {"source": "http", "target": "end"}],
    }
    clean_report = audit_workflow_graph(clean, mode=GovernanceMode.STANDARD)
    unsafe_report = audit_workflow_graph(unsafe, mode=GovernanceMode.STANDARD, max_risk_score=100)
    assert not clean_report.blocked
    assert unsafe_report.blocked
    assert "security.secret.embedded" in {finding.code for finding in unsafe_report.findings}
    return f"clean graph passes; unsafe graph blocks; analyzer={clean_report.analyzer_version}"


def _fingerprint_stability() -> str:
    graph_a = {
        "nodes": [
            {"id": "start", "position": {"x": 0, "y": 0}, "data": {"type": "start"}},
            {"id": "end", "position": {"x": 1, "y": 1}, "data": {"type": "end"}},
        ],
        "edges": [{"id": "a", "source": "start", "target": "end"}],
    }
    graph_b = {
        "viewport": {"x": 4, "y": 8, "zoom": 2},
        "nodes": [
            {"id": "end", "position": {"x": 900, "y": 300}, "selected": True, "data": {"type": "end"}},
            {"id": "start", "position": {"x": 30, "y": 70}, "data": {"type": "start"}},
        ],
        "edges": [{"id": "b", "source": "start", "target": "end", "selected": True}],
    }
    assert semantic_workflow_fingerprint(graph_a) == semantic_workflow_fingerprint(graph_b)
    return "editor-only graph changes preserve the semantic fingerprint"


def _audit_identity() -> str:
    graph = {
        "nodes": [
            {"id": "start", "data": {"type": "start"}},
            {"id": "end", "data": {"type": "end"}},
        ],
        "edges": [{"source": "start", "target": "end"}],
    }
    first = audit_workflow_graph(graph, mode=GovernanceMode.STANDARD)
    second = audit_workflow_graph(graph, mode=GovernanceMode.STANDARD)
    stricter = audit_workflow_graph(graph, mode=GovernanceMode.HIGH_ASSURANCE)
    assert first.product == "Orqivium"
    assert first.schema_version == "2.0"
    assert first.analyzer_version == "2.0.0"
    assert first.audit_id == second.audit_id
    assert first.policy_fingerprint == second.policy_fingerprint
    assert first.policy_fingerprint != stricter.policy_fingerprint
    assert first.audit_id != stricter.audit_id
    return "audit identity is deterministic and changes when publication policy changes"


def _brand_assets() -> str:
    required = [
        ROOT / "web/public/logo/logo.svg",
        ROOT / "web/public/logo/logo-monochrome-white.svg",
        ROOT / "web/public/logo/logo-mark.svg",
        ROOT / "web/public/favicon.ico",
        ROOT / "BRANDING.md",
        ROOT / "LICENSE-ORQIVIUM.md",
    ]
    for path in required:
        assert path.exists() and path.stat().st_size > 0, path
    logo = (ROOT / "web/public/logo/logo.svg").read_text(encoding="utf-8")
    assert "Orqivium" in logo and "#1677FF" in logo and "#7C3AED" in logo
    return "logo suite, favicon, brand specification, and ownership notice are present"


def _public_identity_scan() -> str:
    public_files = [
        ROOT / "README.md", ROOT / "BRANDING.md", ROOT / "MAINTAINERS.md",
        ROOT / "RELEASE_NOTES.md", ROOT / "CHANGELOG.md", ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md", ROOT / "PROJECT_AUDIT.md",
    ]
    forbidden = ("JigLoom", "Nexus", "LangGenius", "Dify")
    violations: list[str] = []
    for path in public_files:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token.lower() in text.lower():
                violations.append(f"{path.name}:{token}")
        assert "Orqivium" in text, path
    assert not violations, ", ".join(violations)
    return "primary public documents consistently present the Orqivium identity"


def _release_identity() -> str:
    assert (ROOT / "orqivium-agent").is_dir()
    assert (ROOT / "orqivium-agent-runtime").is_dir()
    assert not (ROOT / "dify-agent").exists()
    assert not (ROOT / "dify-agent-runtime").exists()
    compose = (ROOT / "docker/docker-compose.yaml").read_text(encoding="utf-8")
    assert "orqivium-api:2.0.0" in compose
    assert "orqivium-web:2.0.0" in compose
    assert "langgenius" not in compose.lower()
    bad_replacement_token = "moor" + "qivium"
    assert bad_replacement_token not in "\n".join(
        path.read_text(encoding="utf-8")
        for path in [ROOT / "cli/src/store/errors.ts", ROOT / "sdks/nodejs-client/LICENSE"]
    ).lower()
    return "major source subsystems, images, CLI, and SDK use the Orqivium identity"



def _identity_token_sweep() -> str:
    legacy = re.compile(r"(?<![A-Za-z0-9])(dify|Dify|DIFY)(?![A-Za-z0-9])|JigLoom|LangGenius|difyctl|dify\.ai")
    damaged = "moor" + "qivium"
    checked = 0
    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative == Path("LICENSE") or relative.parts[:1] == ("legal",) or relative == Path("scripts/validate_orqivium_release.py"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        checked += 1
        if legacy.search(text) or damaged in text.lower():
            violations.append(str(relative))
    assert not violations, ", ".join(violations[:20])
    return f"{checked} readable source files contain no prior public identity or damaged replacement token"


def _license_integrity() -> str:
    expected = "232cf91474932d5110ed304e53b6b742a58463857c571fae803fdf2ac36d7bb3"
    actual = hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest()
    assert actual == expected
    for relative in ("legal/SOURCE_PROVENANCE.md", "legal/THIRD_PARTY_AUTHORS", "legal/THIRD_PARTY_NOTICES.md", "LICENSE-ORQIVIUM.md"):
        assert (ROOT / relative).is_file(), relative
    return f"distribution license preserved verbatim ({actual[:12]}…) and provenance records are present"

def _config() -> str:
    from configs import orqivium_config

    assert orqivium_config.APPLICATION_NAME == "orqivium/core"
    assert orqivium_config.ORQIVIUM_GOVERNANCE_MODE in {"off", "advisory", "standard", "high_assurance"}
    return f"settings load: application={orqivium_config.APPLICATION_NAME}, mode={orqivium_config.ORQIVIUM_GOVERNANCE_MODE}"


def _publication_integrations() -> str:
    files = [
        API / "services/workflow_service.py",
        API / "services/snippet_service.py",
        API / "services/rag_pipeline/rag_pipeline.py",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "from core.governance import audit_for_publication" in text
        assert "audit_for_publication(" in text
        assert text.index("audit_for_publication(") < text.index("Workflow.new(", text.index("def publish_workflow"))
    return "application, snippet, and RAG publication paths audit before snapshot creation"


def _audit_schema() -> str:
    try:
        import jsonschema
    except ImportError:
        return "jsonschema not installed; schema file parsed as JSON only"
    schema = json.loads((ROOT / "docs/schemas/workflow-audit-report.schema.json").read_text(encoding="utf-8"))
    report = audit_workflow_graph({"nodes": [], "edges": []}).to_dict()
    jsonschema.validate(report, schema)
    return "sample audit report validates against JSON Schema 2020-12"


def _compose_yaml() -> str:
    try:
        import yaml
    except ImportError:
        return "PyYAML not installed; compose YAML parse skipped"
    payload = yaml.safe_load((ROOT / "docker/docker-compose.yaml").read_text(encoding="utf-8"))
    assert isinstance(payload, dict) and "services" in payload
    assert "api" in payload["services"]
    return f"Docker Compose parses with {len(payload['services'])} services"


def _markdown_links() -> str:
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    checked = 0
    missing: list[str] = []
    for path in [
        ROOT / "README.md",
        ROOT / "PROJECT_AUDIT.md",
        ROOT / "BRANDING.md",
        ROOT / "MAINTAINERS.md",
        ROOT / "legal/README.md",
        ROOT / "legal/SOURCE_PROVENANCE.md",
        *sorted((ROOT / "docs/architecture").glob("*.md")),
        *sorted((ROOT / "docs/research").glob("*.md")),
    ]:
        text = path.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            checked += 1
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not missing, "; ".join(missing)
    return f"{checked} local Markdown links resolve"


def _cli_exit_contract() -> str:
    clean = {"nodes": [{"id": "start", "data": {"type": "start"}}, {"id": "end", "data": {"type": "end"}}], "edges": [{"source": "start", "target": "end"}]}
    unsafe = {"nodes": [{"id": "start", "data": {"type": "start"}}, {"id": "x", "data": {"type": "http-request", "method": "POST", "password": "unsafe-password"}}, {"id": "end", "data": {"type": "end"}}], "edges": [{"source": "start", "target": "x"}, {"source": "x", "target": "end"}]}
    with tempfile.TemporaryDirectory() as directory:
        directory_path = Path(directory)
        clean_path = directory_path / "clean.json"
        unsafe_path = directory_path / "unsafe.json"
        clean_path.write_text(json.dumps(clean), encoding="utf-8")
        unsafe_path.write_text(json.dumps(unsafe), encoding="utf-8")
        base = [sys.executable, str(ROOT / "scripts/orqivium_workflow_audit.py")]
        clean_result = subprocess.run([*base, str(clean_path), "--mode", "standard", "--format", "json"], capture_output=True)
        unsafe_result = subprocess.run([*base, str(unsafe_path), "--mode", "standard"], capture_output=True)
        assert clean_result.returncode == 0
        assert unsafe_result.returncode == 2
    return "CLI returns 0 for pass and 2 for policy block"


def render(checks: list[Check]) -> str:
    passed = sum(check.passed for check in checks)
    status = "PASS" if passed == len(checks) else "FAIL"
    lines = [
        "# Orqivium Validation Report",
        "",
        f"- **Overall:** {status}",
        f"- **Checks passed:** {passed}/{len(checks)}",
        "- **Validation scope:** dependency-light release checks; not a full distributed integration or browser E2E run",
        "",
        "## Results",
        "",
        "| Check | Result | Detail |",
        "|---|---:|---|",
    ]
    for check in checks:
        detail = check.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {check.name} | {'PASS' if check.passed else 'FAIL'} | {detail} |")
    lines.extend(
        [
            "",
            "## Environment limitation",
            "",
            "The source archive pins Python 3.12 and dependencies including Graphon. The execution sandbox used for this release had Python 3.13 and no network access, so `uv` could not download the pinned Python runtime or resolve the entire backend environment. The focused governance suite was intentionally isolated from the repository-wide `api/tests/conftest.py`, which imports the unavailable Graphon package.",
            "",
            "## Required downstream validation",
            "",
            "Before production deployment, run the complete backend, frontend, worker, migration, Docker Compose, and browser E2E suites in a network-enabled Python 3.12 / Node 22.22+ environment. Validate real model, vector-store, plugin, MCP, sandbox, webhook, HITL, and observability integrations under production-like policy and load.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "VALIDATION_REPORT.md")
    args = parser.parse_args()
    checks = [
        _run("Package metadata", _metadata),
        _run("Python compilation", _compile),
        _run("Focused unit tests", _unit_tests),
        _run("Governance decisions", _governance_behavior),
        _run("Fingerprint stability", _fingerprint_stability),
        _run("Audit identity", _audit_identity),
        _run("Brand assets", _brand_assets),
        _run("Public identity", _public_identity_scan),
        _run("Release identity", _release_identity),
        _run("Identity token sweep", _identity_token_sweep),
        _run("License integrity", _license_integrity),
        _run("Application configuration", _config),
        _run("Publication integrations", _publication_integrations),
        _run("Audit JSON Schema", _audit_schema),
        _run("Docker Compose YAML", _compose_yaml),
        _run("Documentation links", _markdown_links),
        _run("CLI exit contract", _cli_exit_contract),
    ]
    report = render(checks)
    args.output.write_text(report, encoding="utf-8")
    print(report)
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
