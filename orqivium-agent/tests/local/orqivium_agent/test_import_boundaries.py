from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _run_import_check(
    *,
    blocked_imports: list[str],
    imports: list[str],
    assertions: list[str],
    bootstrap: list[str] | None = None,
) -> None:
    python_path = os.pathsep.join([str(PROJECT_ROOT / "src"), os.environ.get("PYTHONPATH", "")])
    module_aliases = {module_name: module_name.replace(".", "_") for module_name in imports}
    script = "\n".join(
        [
            "import builtins",
            "import importlib",
            "import sys",
            f"blocked_imports = {blocked_imports!r}",
            f"imports = {imports!r}",
            f"module_aliases = {module_aliases!r}",
            f"assertions = {assertions!r}",
            "original_import = builtins.__import__",
            "def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):",
            "    for blocked in blocked_imports:",
            "        if name == blocked or name.startswith(f'{blocked}.'):",
            "            raise ModuleNotFoundError(f'blocked import: {name}')",
            "    return original_import(name, globals, locals, fromlist, level)",
            "builtins.__import__ = guarded_import",
            *(bootstrap or []),
            "namespace = {}",
            "for module_name in imports:",
            "    namespace[module_aliases[module_name]] = importlib.import_module(module_name)",
            "for statement in assertions:",
            "    exec(statement, namespace)",
        ]
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = python_path

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def _run_python_script(script: str) -> None:
    python_path = os.pathsep.join([str(PROJECT_ROOT / "src"), os.environ.get("PYTHONPATH", "")])
    env = os.environ.copy()
    env["PYTHONPATH"] = python_path

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_orqivium_agent_root_import_is_client_safe() -> None:
    _run_import_check(
        blocked_imports=[
            "anthropic",
            "orqivium_agent.adapters.llm",
            "orqivium_agent.runtime",
            "orqivium_agent.server",
            "fastapi",
            "google",
            "graphon",
            "openai",
            "pydantic_settings",
            "redis",
        ],
        imports=["orqivium_agent"],
        assertions=[
            "from orqivium_agent import Client",
            "assert orqivium_agent.Client is Client",
            "assert 'Client' in orqivium_agent.__all__",
        ],
    )


def test_protocol_and_orqivium_plugin_exports_do_not_import_server_only_modules() -> None:
    _run_import_check(
        blocked_imports=[
            "anthropic",
            "orqivium_agent.adapters.llm",
            "orqivium_agent.layers.drive.layer",
            "orqivium_agent.layers.execution_context.layer",
            "orqivium_agent.layers.ask_human.layer",
            "orqivium_agent.layers.orqivium_plugin.llm_layer",
            "orqivium_agent.layers.orqivium_plugin.tools_layer",
            "orqivium_agent.layers.knowledge.client",
            "orqivium_agent.layers.knowledge.layer",
            "orqivium_agent.layers.output.output_layer",
            "orqivium_agent.layers.shell.layer",
            "orqivium_agent.runtime",
            "orqivium_agent.server",
            "fastapi",
            "google",
            "graphon",
            "openai",
            "pydantic_settings",
            "redis",
            "shellctl.client",
        ],
        imports=[
            "orqivium_agent.protocol",
            "orqivium_agent.layers.drive",
            "orqivium_agent.layers.execution_context",
            "orqivium_agent.layers.ask_human",
            "orqivium_agent.layers.orqivium_plugin",
            "orqivium_agent.layers.knowledge",
            "orqivium_agent.layers.output",
            "orqivium_agent.layers.shell",
        ],
        assertions=[
            "assert hasattr(orqivium_agent_protocol, 'CreateRunRequest')",
            "assert hasattr(orqivium_agent_layers_drive, 'OrqiviumDriveLayerConfig')",
            "assert hasattr(orqivium_agent_layers_execution_context, 'OrqiviumExecutionContextLayerConfig')",
            "assert hasattr(orqivium_agent_layers_ask_human, 'OrqiviumAskHumanLayerConfig')",
            "assert hasattr(orqivium_agent_layers_orqivium_plugin, 'OrqiviumPluginLLMLayerConfig')",
            "assert hasattr(orqivium_agent_layers_knowledge, 'OrqiviumKnowledgeBaseLayerConfig')",
            "assert hasattr(orqivium_agent_layers_output, 'OrqiviumOutputLayerConfig')",
            "assert hasattr(orqivium_agent_layers_shell, 'OrqiviumShellLayerConfig')",
        ],
    )


def test_agent_cli_help_import_is_client_safe() -> None:
    _run_import_check(
        blocked_imports=[
            "orqivium_agent.server",
            "orqivium_agent.agent_stub.server",
            "fastapi",
            "google.protobuf",
            "grpclib",
            "jwcrypto",
            "pydantic_settings",
            "redis",
        ],
        imports=[
            "orqivium_agent.agent_stub.protocol",
            "orqivium_agent.layers._agent_cli_help",
            "orqivium_agent.agent_stub.shell_env",
            "orqivium_agent.layers.shell.layer",
            "orqivium_agent.runtime.compositor_factory",
        ],
        assertions=[
            "assert hasattr(orqivium_agent_agent_stub_protocol, 'AgentStubConnectRequest')",
            "assert hasattr(orqivium_agent_layers__agent_cli_help, 'render_agent_stub_cli_help')",
            "assert hasattr(orqivium_agent_agent_stub_shell_env, 'build_shell_agent_stub_env')",
            "assert hasattr(orqivium_agent_layers_shell_layer, 'OrqiviumShellLayer')",
            "assert hasattr(orqivium_agent_runtime_compositor_factory, 'create_default_layer_providers')",
        ],
        bootstrap=[
            "import types",
            "if 'graphon.model_runtime.entities.llm_entities' not in sys.modules:",
            "    graphon_module = types.ModuleType('graphon')",
            "    model_runtime_module = types.ModuleType('graphon.model_runtime')",
            "    entities_module = types.ModuleType('graphon.model_runtime.entities')",
            "    llm_entities_module = types.ModuleType('graphon.model_runtime.entities.llm_entities')",
            "    message_entities_module = types.ModuleType('graphon.model_runtime.entities.message_entities')",
            "    llm_entities_module.LLMResultChunk = type('LLMResultChunk', (), {})",
            "    llm_entities_module.LLMUsage = type('LLMUsage', (), {})",
            "    for name in ('AssistantPromptMessage', 'AudioPromptMessageContent', 'DocumentPromptMessageContent', 'ImagePromptMessageContent', 'PromptMessage', 'PromptMessageContentUnionTypes', 'PromptMessageTool', 'SystemPromptMessage', 'TextPromptMessageContent', 'ToolPromptMessage', 'UserPromptMessage', 'VideoPromptMessageContent'):",
            "        setattr(message_entities_module, name, type(name, (), {}))",
            "    sys.modules['graphon'] = graphon_module",
            "    sys.modules['graphon.model_runtime'] = model_runtime_module",
            "    sys.modules['graphon.model_runtime.entities'] = entities_module",
            "    sys.modules['graphon.model_runtime.entities.llm_entities'] = llm_entities_module",
            "    sys.modules['graphon.model_runtime.entities.message_entities'] = message_entities_module",
            "    graphon_module.model_runtime = model_runtime_module",
            "    model_runtime_module.entities = entities_module",
            "    entities_module.llm_entities = llm_entities_module",
            "    entities_module.message_entities = message_entities_module",
            "if 'jsonschema' not in sys.modules:",
            "    jsonschema_module = types.ModuleType('jsonschema')",
            "    jsonschema_exceptions_module = types.ModuleType('jsonschema.exceptions')",
            "    jsonschema_protocols_module = types.ModuleType('jsonschema.protocols')",
            "    jsonschema_validators_module = types.ModuleType('jsonschema.validators')",
            "    class _SchemaError(Exception):",
            "        pass",
            "    class _ValidationError(Exception):",
            "        path = ()",
            "    class _Validator:",
            "        @staticmethod",
            "        def check_schema(schema):",
            "            return None",
            "        def __init__(self, schema):",
            "            self.schema = schema",
            "        def iter_errors(self, value):",
            "            return iter(())",
            "    def _validator_for(schema):",
            "        return _Validator",
            "    jsonschema_module.SchemaError = _SchemaError",
            "    jsonschema_exceptions_module.ValidationError = _ValidationError",
            "    jsonschema_protocols_module.Validator = _Validator",
            "    jsonschema_validators_module.validator_for = _validator_for",
            "    sys.modules['jsonschema'] = jsonschema_module",
            "    sys.modules['jsonschema.exceptions'] = jsonschema_exceptions_module",
            "    sys.modules['jsonschema.protocols'] = jsonschema_protocols_module",
            "    sys.modules['jsonschema.validators'] = jsonschema_validators_module",
        ],
    )


def test_agent_cli_help_render_does_not_load_server_or_cli_modules() -> None:
    blocked_modules = [
        "orqivium_agent.server",
        "orqivium_agent.agent_stub.server",
        "fastapi",
        "google.protobuf",
        "grpclib",
        "jwcrypto",
        "pydantic_settings",
        "redis",
    ]
    script = "\n".join(
        [
            "import importlib",
            "import sys",
            f"blocked_modules = {blocked_modules!r}",
            'module = importlib.import_module("orqivium_agent.layers._agent_cli_help")',
            'help_text = module.render_agent_stub_cli_help(("config",))',
            'assert "Inspect or update Agent Soul-backed config assets" in help_text',
            'assert "typer" not in sys.modules',
            'assert "click" not in sys.modules',
            "loaded_blocked = sorted(",
            "    name",
            "    for name in sys.modules",
            '    if any(name == blocked or name.startswith(f"{blocked}.") for blocked in blocked_modules)',
            ")",
            "assert loaded_blocked == [], loaded_blocked",
        ]
    )
    _run_python_script(script)


def test_shellctl_client_imports_do_not_import_server_modules() -> None:
    _run_import_check(
        blocked_imports=[
            "aiosqlite",
            "fastapi",
            "sqlalchemy",
            "sqlmodel",
            "uvicorn",
        ],
        imports=["shellctl", "shellctl.client", "shellctl.shared"],
        assertions=[
            "assert hasattr(shellctl, 'ShellctlClient')",
            "assert hasattr(shellctl_client, 'ShellctlClient')",
            "assert hasattr(shellctl_shared, 'JobResult')",
        ],
    )


def test_server_settings_import_does_not_import_agent_stub_app() -> None:
    try:
        __import__("pydantic_settings")
        __import__("jwcrypto")
    except ModuleNotFoundError:
        pytest.skip("server extras are not installed in this environment")

    _run_import_check(
        blocked_imports=["orqivium_agent.agent_stub.server.app"],
        imports=["orqivium_agent.server.settings"],
        assertions=["assert hasattr(orqivium_agent_server_settings, 'ServerSettings')"],
    )


def test_agenton_collection_roots_do_not_eagerly_import_pydantic_ai_implementations() -> None:
    _run_import_check(
        blocked_imports=[
            "agenton_collections.layers.pydantic_ai",
            "agenton_collections.transformers.pydantic_ai",
        ],
        imports=["agenton_collections", "agenton_collections.transformers"],
        assertions=[
            "assert 'PydanticAIBridgeLayer' not in agenton_collections.__all__",
            "assert agenton_collections_transformers.__all__ == []",
        ],
    )
